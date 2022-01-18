from enum import Enum
from ctypes import c_int32, c_uint32
from typing import Union
import pdb
import json
import os
import logging

from Pyssembler.mips.mips_program import ProgramLine
from ..hardware import Integer
from Pyssembler.mips import utils
from ..hardware import registers
from ..tokenizer import TokenType, tokenize_instr_format
from ..errors import AssemblerError

__PSEUDO_INSTRS_FILE__ = os.path.dirname(__file__)+'/pseudo_instructions.json'
__BASIC_INSTRS_FILE__ = os.path.dirname(__file__)+'/instructions.json'
__LOGGER__ = logging.getLogger('Pyssembler.Instruction')


class InstructionType(Enum):

    R_TYPE = 0
    I_TYPE = 1
    B_TYPE = 2
    J_TYPE = 3
    J_SHIFT_TYPE = 4


__TYPE_MATCH__ = {
    'R': InstructionType.R_TYPE,
    'I': InstructionType.I_TYPE,
    'B': InstructionType.B_TYPE,
    'J': InstructionType.J_TYPE,
    'JS': InstructionType.J_SHIFT_TYPE
}


class Instruction:
    """
    Base class for MISP32 instructions
    """

    def __init__(self, mnemonic, format_: str):
        self.format = format_
        self.fmt_tokens = tokenize_instr_format(self.format)
        self.mnemonic = mnemonic

    def match(self, instr: ProgramLine) -> bool:
        """
        Returns True if the tokens in line matches our fmt tokens
        """

        if instr.tokens[0].value != self.mnemonic:
            return False
        if len(instr.tokens)-1 != len(self.fmt_tokens):
            # Ignore mnemonic in instr token list
            return False
        for instr_token, fmt_token in zip(instr.tokens[1:], self.fmt_tokens):
            if fmt_token.type == TokenType.IMMEDIATE:
                # Expecting an immediate OR a label
                if not instr_token.type in (TokenType.IMMEDIATE, TokenType.LABEL):
                    return False
            elif instr_token.type != fmt_token.type:
                return False
        return True


class BasicInstruction(Instruction):
    """
    Base class for supported MIPS32 instructions
    """

    def __init__(self, mnemonic, format_, encoding, description, type_) -> None:
        """
        Initializes a MIPS32 Instruction

        Parameters
        ----------
        mnemonic : str
            The mnemonic of the instruction
        format_ : str
            How the instruction should be formatted
        encoding : str
            Binary string used to encode the instruction into binary.
            The bit values in this string are used to match a binary
            instruction to this type.

            Encodings may have the following placeholders
                rd, rs, rt - 5-bit register addresses
                imm - n bit immediate
        description : str
            A description of the instruction
        type_ : InstructionType
            The type of instruction
        """

        super().__init__(mnemonic, format_)
        self.encoding = encoding
        self.description = description
        self.type = type_
        self.mask = ''
        self.match_value = 0

    def match_by_mnemonic(self, mnemonic: str) -> bool:
        """
        Returns true if the mnemonic matches this instruction
        """
        return self.mnemonic == mnemonic

    def generate_example(self, bstring: bool = False) -> Union[int, str]:
        """
        Generate an example binary instruction of this type

        Parameters
        ----------
        bstring : bool, optional
            If true, return the instruction as a binary string
        """
        rs = 31
        rt = 31
        rd = 31
        imm = 0
        if self.comp_regs == False:
            rt = 30
        if bstring:
            return self.encoding.format(rs=rs, rt=rt, rd=rd, imm=imm)
        return int(self.encoding.format(rs=rs, rt=rt, rd=rd, imm=imm))

    def encode(self, line: ProgramLine, bstring=False) -> Union[int, str]:
        """
        Encodes the passed program line into binary

        Assumes the line has already been tokenized

        Parameters
        ----------
        line : ProgramLine
            the line to be encoded
        bstring : bool, optional
            If true, return the encoded instruction as a binary string

        Returns
        -------
        Union[int, str]
            The encoded instruction as an int or string. Returns None if 
            something went wrong
        """

        if not self.match_by_mnemonic(line.tokens[0].value):
            # line is not of this type
            return None
        __LOGGER__.debug(f'Encoding {line.clean_line}...')
        if len(self.fmt_tokens) != len(line.tokens)-1:
            # number of tokens in line should match number of format tokens
            __LOGGER__.debug('Unexpected number of tokens, cannot encode instruction!')
            return None

        values = {
            'rd': None,
            'rs': None,
            'rt': None,
            'immediate': None
        }
        for fmt_token, instr_token in zip(self.fmt_tokens, line.tokens[1:]):
            if not fmt_token.value in values:
                # fmt_token signifies a parenthesis or potential
                # other non-value token, raise error if fmt_token != instr_token
                if fmt_token.value != instr_token.value:
                    __LOGGER__.debug('Invalid token encountered, raising AssemblerError')
                    raise AssemblerError(
                        filename=line.filename,
                        linenum=line.linenum,
                        charnum=instr_token.charnum,
                        message='Invalid Syntax')
                continue

            if fmt_token.type == TokenType.IMMEDIATE:
                # We need to encode an immediate. This is a little more
                # complicated since we have to deal with differing bit amounts
                # and that the instruction token can be an immediate OR a label
                # Normally I'd use python's format(i, '016b') to convert an int
                # to a binary string, but I found that passing an int too big will
                # return more than 16 bits, even though '016b' should format the
                # binary string as 16 bits. self.get_encoding_imm_size() will return
                # the number of bits reserved for the immediate, so use that to get
                # the right number of bits from an immediate value. This also allows
                # for ignoring any excess bits if the user tries to use an immediate
                # too large. For example if an immediate is passed that is larger than
                # 16 bits and we have to encode 16 bits, only the lower 16 bits will
                # be encoded
                imm = 0
                if instr_token.type == TokenType.LABEL:
                    # Instruction token is a label, convert it to immediate
                    print(line.program.get_local_symbols(line))
                    print(line.program.global_symbols)
                    if line.program.get_local_symbols(line).has(instr_token.value):
                        imm = line.program.get_local_symbols(
                            line).get(instr_token.value)
                    elif line.program.global_symbols.has(instr_token.value):
                        imm = line.program.global_symbols.get(
                            instr_token.value)
                    else:
                        # Symbol does not exist
                        raise AssemblerError(
                            filename=line.filename,
                            linenum=line.linenum,
                            charnum=instr_token.charnum,
                            message='Label was never declared/defined in this scope')
                    if self.type == InstructionType.J_SHIFT_TYPE:
                        # For J-Shift Types, imm is the address of label >> 2
                        imm = imm >> 2
                        line.operands.append(imm)
                    elif self.type == InstructionType.B_TYPE:
                        # For B-Types, imm is the signed offset between the target address
                        # and the next instruction's address
                        imm = (imm - line.memory_addr - 4) >> 2
                        line.operands.append(imm)
                        imm = c_uint32(imm).value
                    elif self.type == InstructionType.I_TYPE:
                        line.operands.append(imm)
                elif instr_token.type == TokenType.IMMEDIATE:
                    # Instruction token is an immediate, get the value
                    imm = instr_token.value
                    line.operands.append(imm)
                num_bits = self.get_encoding_imm_size()
                if num_bits is None:
                    # This shouldn't happen. If a fmt token type is immediate, then
                    # there should be an imm format field in the encoding
                    raise AssemblerError(
                        filename=line.filename,
                        linenum=line.linenum,
                        charnum=instr_token.charnum,
                        message='Internal Error')
                if imm < 0:
                    # if imm is less than zero, get unsigned value from signed bits
                    imm = c_uint32(imm).value
                imm = Integer.get_bits(imm, 0, num_bits-1)
                values[fmt_token.value] = imm
            elif fmt_token.type != instr_token.type:
                # The first if statement is the only case where token types
                # should differ
                raise AssemblerError(
                    filename=line.filename,
                    linenum=line.linenum,
                    charnum=instr_token.charnum,
                    message='Expected a(n) {}'.format(fmt_token.type.name))
            elif instr_token.type == TokenType.IMMEDIATE:
                # If immediate is negative, python likes to format negative binary as
                # -0b010101 instead of signed/unsigned
                # Use c_uint32 to do conversion from signed value to unsigned value
                imm = c_uint32(instr_token.value).value
                values[fmt_token.value] = imm
                line.operands.append(imm)
            else:
                values[fmt_token.value] = instr_token.value
                line.operands.append(instr_token.value)

        res = self.encoding.format(rd=values['rd'], rt=values['rt'], rs=values['rs'],
                                   imm=values['immediate'])
        if bstring:
            return res
        return int(res, 2)

    def get_encoding_imm_size(self):
        in_imm_format = False

        current = ''
        for c in self.encoding:
            if in_imm_format:
                if c == 'b':
                    # End of imm format
                    break
                current += c
            if c == 'i':
                current += c
                in_imm_format = True
        if current:
            return int(current.split(':')[1])
        return None

    def __str__(self) -> str:
        return 'MIPS32 INSTRUCTION: '+self.mnemonic

    def __repr__(self) -> str:
        return 'MIPS32 INSTRUCTION: mnemonic={}, formatting={}, encoding={}'.format(self.mnemonic, self.format,
                                                                                    self.encoding)


class PseudoInstruction(Instruction):
    """
    Base class for supported MIPS32 pseudo instructions
    """

    def __init__(self, format_: str, name: str, desc: str, expanded_instrs: list) -> None:

        super().__init__(format_.split()[0], format_)
        self.name = name
        self.description = desc
        self.expanded_instructions = expanded_instrs

    def expand(self, line: ProgramLine) -> list:
        """Expand the pseudo instruction into MIPS32 Instructions

        Returns
        -------
        list
            The list of expanded instructions
        """

        expanded = []
        for exp_instr in self.expanded_instructions:
            for i, token in enumerate(self.fmt_tokens, start=1):
                if line.tokens[i].type == TokenType.REGISTER:
                    # This will have been converted from reg name ($s1) to int addres
                    # Need to go back to name
                    exp_instr = exp_instr.replace(
                        token.value, 
                        registers.get_name_from_address(line.tokens[i].value))
                else:
                    exp_instr = exp_instr.replace(token.value, str(line.tokens[i].value))
            expanded.append(exp_instr)
        return expanded

    def __str__(self) -> str:
        return 'MIPS32 PSEUDO INSTRUCTION '+self.mnemonic

    def __repr__(self) -> str:
        return 'MIPS32 INSTRUCTION: mnemonic={}, formatting={}, expand={}'.format(self.mnemonic, self.format,
                                                                                  self.expanded_instructions)


def generate_basic_instructions():
    output = []
    with open(__BASIC_INSTRS_FILE__, 'r') as f:
        for mnemonic, instr in json.load(f).items():
            output.append(BasicInstruction(
                mnemonic, instr['format'], instr['encoding'],
                instr['description'], __TYPE_MATCH__[instr['type']]))
    return output


def generate_pseudo_instructions():
    output = []
    with open(__PSEUDO_INSTRS_FILE__, 'r') as f:
        for instr, info in json.load(f).items():
            name = info['name']
            desc = info['description']
            expanded_instrs = info['expansion']
            output.append(PseudoInstruction(instr, name, desc, expanded_instrs))
    return output
