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
INSTR_PSUEDO = ['beqz', 'blt', 'bge', 'bgt', 'ble',
                'clear', 'la', 'li', 'move', 'mul']
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

def mips_to_binary(code):
    '''
    Function for converting a list of MIPS instructions
    into a list of binary instructions
    '''
    log.debug('Preparing translation: MIPS -> Binary...')
    code = clean_code(code)
    REG = {value: key for key, value in __open_reg().items()}
    BINS = __open_encodings("BINS")
    result = []

    log.debug('Expanding psuedo-instructions...')
    cnt = 0
    while cnt < len(code):
        line = line = code[cnt][0]
        mips = line.split()
        if ':' in mips[0]:
            mips.pop(0)
        instr = mips[0]
        if instr in INSTR_PSUEDO:
            if instr == 'move':
                code[cnt] = ('or {}, {}, $zero'.format(mips[1], mips[2]), None)
            elif instr == 'clear':
                code[cnt] = ('or {}, $zero, $zero'.format(mips[1]), None)
            elif instr == 'li':
                code[cnt] = ('ori {}, $zero, {}'.format(mips[1], mips[2]), None)
            elif instr == 'b':
                code[cnt] = ('beq $zero, $zero, {}'.format(mips[1]), None)
            elif instr == 'bal':
                code[cnt] = ('bgezal $zero, {}'.format(mips[1]), None)
            elif instr == 'bgt':
                code[cnt] = ('slt $at, {}, {}'.format(mips[2], mips[1]), None)
                code.insert(cnt+1, ('bne $at, $zero, {}'.format(mips[3]), None))
            elif instr == 'blt':
                code[cnt] = ('slt $at, {}, {}'.format(mips[1], mips[2]), None)
                code.insert(cnt+1, ('bne $at, $zero, {}'.format(mips[3]), None))
            elif instr == 'bge':
                code[cnt] = ('slt $at, {}, {}'.format(mips[1], mips[2]), None)
                code.insert(cnt+1, ('beq $at, $zero, {}'.format(mips[3]), None))
            elif instr == 'ble':
                code[cnt] = ('slt $at, {}, {}'.format(mips[2], mips[1]), None)
                code.insert(cnt+1, ('beq $at, $zero, {}'.format(mips[3]), None))
        cnt += 1
    log.debug('Expanded psuedo-instructions!')

    log.debug('Locating labels...')
    labels = {}
    cnt = 0
    for line in code:
        line = line[0]
        if ':' in line:
            labels[line.split()[0].replace(':', '')] = cnt
        cnt += 1
    log.debug("Found {} data labels!".format(len(labels.keys())))

    log.debug("Preparations complete! Starting line-by-line translations...")
    cnt = 0
    while cnt < len(code):
        line = code[cnt][0]
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
        try:
            if instr == "noop":
                result.append(BINS[instr])
                cnt += 1
                continue

            elif instr == 'syscall':
                result.append(BINS[instr])
                cnt += 1
                continue

            elif instr in INSTR_PARENTHESIS:
                reg1 = REG.get(mips[1])
                reg2 = REG.get(mips[2].split('(')[1].replace(')', ''))
                if reg1 is None:
                    raise InvalidRegisterError(line, code[cnt][1], mips[1])
                elif reg2 is None:
                    raise InvalidRegisterError(line, code[cnt][1], mips[2].split('(')[1].replace(')', ''))
                i_16 = binary(mips[2].split('(')[0], 16)

            elif instr in INSTR_BRANCH:
                reg1 = REG.get(mips[1])
                if reg1 is None:
                    raise InvalidRegisterError(line, code[cnt][1], mips[1])
                if instr == 'beq' or instr == 'bne':
                    reg2 = REG.get(mips[2])
                    if reg2 is None:
                        raise InvalidRegisterError(line, code[cnt][1], mips[2])
                offset = labels.get(mips[len(mips)-1])
                if offset is None:
                    raise InvalidLabelError(line, code[cnt][1], mips[len(mips)-1])
                sub_one = cnt < offset
                offset = offset - cnt
                if sub_one:
                    offset -= 1
                i_16 = binary(offset, 16)
                print(offset)

            elif instr in INSTR_J:
                target = labels.get(mips[1])
                if target is None:
                    raise InvalidLabelError(line, code[cnt][1], mips[1])
                i_26 = binary(target, 26)

            elif instr in INSTR_0:
                reg1 = REG.get(mips[1])
                if reg1 is None:
                    raise InvalidRegisterError(line, code[cnt][1], mips[1])
            
            elif instr in INSTR_012:
                reg1 = REG.get(mips[1])
                reg2 = REG.get(mips[2])
                reg3 = REG.get(mips[3])
                if reg1 is None:
                    raise InvalidRegisterError(line, code[cnt][1], mips[1])
                elif reg2 is None:
                    raise InvalidRegisterError(line, code[cnt][1], mips[2])
                elif reg3 is None:
                    raise InvalidRegisterError(line, code[cnt][1], mips[3])
            
            elif instr in INSTR_013:
                reg1 = REG.get(mips[1])
                reg2 = REG.get(mips[2])
                if reg1 is None:
                    raise InvalidRegisterError(line, code[cnt][1], mips[1])
                elif reg2 is None:
                    raise InvalidRegisterError(line, code[cnt][1], mips[2])
                i_16 = binary(mips[3], 16)
            
            elif instr in INSTR_01:
                reg1 = REG.get(mips[1])
                reg2 = REG.get(mips[2])
                if reg1 is None:
                    raise InvalidRegisterError(line, code[cnt][1], mips[1])
                elif reg2 is None:
                    raise InvalidRegisterError(line, code[cnt][1], mips[2])
            
            elif instr in INSTR_015:
                reg1 = REG.get(mips[1])
                reg2 = REG.get(mips[2])
                if reg1 is None:
                    raise InvalidRegisterError(line, code[cnt][1], mips[1])
                elif reg2 is None:
                    raise InvalidRegisterError(line, code[cnt][1], mips[2])
                i_5 = binary(mips[3], 5)
            
            else:
                raise InvalidInstructionError(code[cnt][0], code[cnt][1], instr)
        except InvalidMIPSInstructionError as e:
            return (e, False)
        except Exception as e:
            return (InvalidMIPSInstructionError(line, code[cnt][1]), False)

        result.append(BINS[instr].format(reg1, reg2, reg3, i_16, i_26, i_5))
        cnt += 1
    log.debug("Completed line-by-line translations!")
    return (result, True)

