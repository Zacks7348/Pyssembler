# pylint: disable=E1101

import json
import logging

from Pyssembler.environment.helpers import integer, binary, clean_code
from Pyssembler.config import Config
from Pyssembler.errors import *

log = logging.getLogger(__name__)

REGISTERS = "Pyssembler/lib/language/mips/registers.json"
TEMPLATES = "Pyssembler/lib/language/mips/encodings.json"

#
# INSTRUCTIONS CATEGORIZED BY ENCODING
#
INSTR_PARENTHESIS = ['lb', 'lw', 'sb', 'sw']
INSTR_BRANCH = [
    'beq', 'bgez', 'bgezal', 'bgtz', 
    'blez', 'bltz', 'bltzal', 'bne'
]
INSTR_J = ['j', 'jal']
INSTR_0 = ['jr', 'mfhi', 'mflo']
INSTR_012 = [
    'add', 'addu', 'and', 'or', 'sllv', 'slt', 
    'sltu', 'srlv', 'sub', 'subu', 'xor'
]
INSTR_013 = [
    'addi', 'addiu', 'andi', 'ori', 
    'slti', 'sltiu', 'xori' 
]
INSTR_01 = ['div', 'divu', 'mult', 'multu']
INSTR_015 = ['sll', 'sra', 'srl']

BRANCHES = ['000100', '000001', '000111', '000110', '000101']
JUMPS = ['000010', '000011']

def __open_encodings(key):
    with open(TEMPLATES, "r") as output:
        return json.load(output)[key]

def __open_reg():
    with open(REGISTERS, 'r') as output:
        return json.load(output)

def verify_binary(line, line_num, length):
    opcodes = __open_encodings("OPCODES")
    if len(line) != 32:
        raise InvalidSizeError(line, line_num)
    if line[:6] not in opcodes.keys():
        raise InvalidOperationError(line, line_num, line[:6])
    if line[:6] == "000000":
        if line[26:] not in opcodes[line[:6]].keys():
            raise InvalidFunctionError(line, line_num, line[26:])
    if line[:6] in JUMPS:
        if integer(line[6:]) < 0 or integer(line[6:]) > length:
            raise InvalidTargetError(line, line_num, line[6:])
    if line[:6] in BRANCHES:
        offset = integer(line[16:], complement=True)+line_num
        if offset < 0 or offset > length:
            raise InvalidOffsetError(line, line_num, line[16:])

def verify_mips(line, line_num, labels):
    REG = {value: key for key, value in __open_reg().items()}
    mips = line.replace(',', '').split()
    if ':' in mips[0]:
        if mips[0].replace(':', '') not in labels.keys():
            raise InvalidLabelError(line, line_num, mips[0].replace(':', ''))
        mips.pop(0)
    if mips[0] in INSTR_PARENTHESIS:
        error = (False, None)
        if tmp := mips[1] not in REG.keys():
            error = (True, tmp)
        elif tmp := mips[2].split('(')[1].replace(')', '') not in REG.keys():
            error = (True, tmp)
        if error[0]:
            raise InvalidRegisterError(line, line_num, error[1])

def mips_to_binary(code):
    """
    Function for converting a list of MIPS instructions
    into a list of Binary instructions
    """

    log.debug("Preparing translation: MIPS -> Binary...")
    REG = {value: key for key, value in __open_reg().items()}
    BINS = __open_encodings("BINS")
    result = []

    log.debug("Locating labels...")
    labels = {}
    cnt = 0
    for line in code:
        if ':' in line:
            labels[line.split()[0].replace(':', '')] = cnt
        cnt += 1
    log.debug("Found {} labels!".format(len(labels.keys())))

    log.debug("Validating MIPS instructions...")
    #TODO: validate each instruction, raise exception on error
    log.debug("Validated MIPS instructions!")

    log.debug("Preparations complete! Starting line-by-line translations...")
    cnt = 0
    for line in code:
        mips = line.replace(',', '').split()
        if ':' in mips[0]:
            mips.pop(0)
        instr = mips[0]
        reg1 = None
        reg2 = None
        reg3 = None
        i_16 = None
        i_26 = None
        i_5 =  None
        
        if instr == "noop":
            result.append(BINS[instr])
            continue

        elif instr == 'syscall':
            result.append(BINS[instr])
            continue
        
        elif instr in INSTR_PARENTHESIS:
            reg1 = REG[mips[1]]
            reg2 = REG[mips[2].split('(')[1].replace(')', '')]
            i_16 = binary(mips[2].split('(')[0], 16)

        elif instr in INSTR_BRANCH:
            reg1 = REG[mips[1]]
            if instr == 'beq' or instr == 'bne':
                reg2 = REG[mips[2]]
            offset = labels[mips[len(mips)-1]] - cnt
            i_16 = binary(offset, 16)

        elif instr in INSTR_J:
            i_26 = binary(labels[mips[1]], 26)

        elif instr in INSTR_0:
            reg1 = REG[mips[1]]
        
        elif instr in INSTR_012:
            reg1 = REG[mips[1]]
            reg2 = REG[mips[2]]
            reg3 = REG[mips[3]]
        
        elif instr in INSTR_013:
            reg1 = REG[mips[1]]
            reg2 = REG[mips[2]]
            i_16 = binary(mips[3], 16)
        
        elif instr in INSTR_01:
            reg1 = REG[mips[1]]
            reg2 = REG[mips[2]]
        
        elif instr in INSTR_015:
            reg1 = REG[mips[1]]
            reg2 = REG[mips[2]]
            i_5 = binary(mips[3], 5)

        result.append(BINS[instr].format(reg1, reg2, reg3, i_16, i_26, i_5))
        cnt += 1
    return result   

def binary_to_mips(code):
    log.debug("Preparing translation: Binary -> MIPS")
    code = clean_code(code)
    REG = __open_reg()
    OPCODE = __open_encodings("OPCODES")
    result = []

    log.debug("Generating labels...")
    labels={}
    label_cnt = 1
    label_name = Config().translator_config["label-name"]
    cnt = 0
    for line in code:
        if line[:6] in BRANCHES:
            target = integer(line[16:], complement=True) + cnt
            if not target in labels.keys():
                labels[target] = "{}{}".format(label_name, label_cnt)
                label_cnt += 1
        elif line[:6] in JUMPS:
            target = integer(line[6:])
            if not target in labels.keys():
                labels[target] = "{}{}".format(label_name, label_cnt)
                label_cnt += 1
        cnt += 1
    log.debug('Generated {} labels!'.format(len(labels.keys())))

    log.debug('Starting line-by-line translations')
    cnt = 0
    for line in code:
        try:
            verify_binary(line, cnt, len(code))
        except TranslationError as e:
            log.debug("Error on line "+str(cnt))
            return e
        instr = line[:6]
        i_16 = integer(line[16:], complement=True)
        i_5 = integer(line[21:26], complement=True)
        label = None
        if instr in BRANCHES:
            label = labels[integer(line[16:], complement=True) + cnt]
        elif instr in JUMPS:
            label = labels[integer(line[6:], complement=True)]

        try:
            reg1 = REG[line[6:11]]
        except:
            reg1 = None
        try:
            reg2 = REG[line[11:16]]
        except:
            reg2 = None
        try:
            reg3 = REG[line[16:21]]
        except:
            reg3 = None

        if instr == "000000" or instr == "000001":
            result.append(OPCODE[instr][line[26:]].format(reg1, reg2, reg3, i_16, i_5, label))
        else:
            result.append(OPCODE[instr].format(reg1, reg2, reg3, i_16, i_5, label))
        cnt += 1
    log.debug("Completed line-by-line translations!")
    
    log.debug("Inserting labels...")
    for key, value in labels.items():
        result[key] = "{}: {}".format(value, result[key])
    log.debug("Inserted labels!")
    return result
