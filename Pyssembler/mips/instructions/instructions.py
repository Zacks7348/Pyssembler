from Pyssembler.mips.mips_program import ProgramLine
from enum import Enum
from ctypes import c_int32, c_uint32
from typing import Union
import pdb

from ..utils import Integer
from Pyssembler.mips import utils
from ..hardware import registers
from ..tokenizer import TokenType, tokenize_instr_format
from ..errors import AssemblerError


class InstructionType(Enum):

    R_TYPE = 0
    I_TYPE = 1
    B_TYPE = 2
    J_TYPE = 3
    J_SHIFT_TYPE = 4


class Instruction:
    """
    Base class for supported MIPS32 instructions
    """

    def __init__(self, format_, encoding, description, type_, comp_regs=None,
                 reg1_zero=True, reg2_zero=True, reg1_lt_reg2=False) -> None:
        """
        Initializes a MIPS32 Instruction

        Parameters
        ----------
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
        comp_regs : bool, None, optional
            Defines how an instruction should be identified
            None - Ignore register fields
            True - Reg1 and Reg2 should be the same value
            False - Reg1 and Reg2 should have different values
        reg1_zero : bool, optional
            Declares whether or not this instruction's reg1 field can be zero (True-can be zero, False-cannot be zero) (Default=True)
        reg2_zero : bool, optional
            Declares whether or not this instruction's reg2 field can be zero (True-can be zero, False-cannot be zero) (Default=True)
        reg1_lt_reg2 : bool, optional
            Declares whether or not this instruction's reg1 field must be less than reg2 field (Default=False)
        """
        self.format = format_
        self.mnemonic = self.format.split()[0]
        self.encoding = encoding
        self.description = description
        self.type = type_
        self.mask = ''
        self.match_value = 0
        self.comp_regs = comp_regs
        self.reg1_zero = reg1_zero
        self.reg2_zero = reg2_zero
        self.reg1_lt_reg2 = reg1_lt_reg2
        self.__generate_match_value_and_mask()

    def match(self, instr: int) -> bool:
        """
        Returns true if the binary instruction matches this instruction type
        """
        res = (instr & self.mask) == self.match_value
        if not res:
            return False

        if self.comp_regs is None:
            pass
        elif self.comp_regs:
            # reg1 and reg2 should be the same value
            res = utils.get_reg1(instr) == utils.get_reg2(instr)
        elif not self.comp_regs:
            # reg1 and reg2 should have different values
            #print('\t\t{0:05b} != {1:05b}'.format(utils.get_reg1(instr), utils.get_reg2(instr)))
            res = utils.get_reg1(instr) != utils.get_reg2(instr)
        if not res:
            return False

        if not self.reg1_zero:
            # reg1 cannot be zero
            res = utils.get_reg1(instr) != 0
        if not res:
            return False
        if not self.reg2_zero:
            # reg2 cannot be zero
            res = utils.get_reg2(instr) != 0
        return res

    def match_by_mnemonic(self, mnemonic: str) -> bool:
        """
        Returns true if the mnemonic matches this instruction
        """
        return self.mnemonic == mnemonic

    def __generate_match_value_and_mask(self):
        self.match_value = int(
            self.encoding.format(rd=0, rt=0, rs=0, imm=0), 2)
        in_ph = False
        for c in self.encoding:
            if in_ph:
                if c == '}':
                    in_ph = False
                self.mask += c
            else:
                if c == '{':
                    in_ph = True
                    self.mask += c
                elif c in '01':
                    self.mask += '1'
                else:
                    # Invalid char in encoding, shouldn't happen
                    raise ValueError('Invalid encoding for instruction!')
        self.mask = self.mask.format(rd=0, rt=0, rs=0, imm=0)
        while len(self.mask) < 32:
            self.mask += '0'
        self.mask = int(self.mask, 2)

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
        format_tokens = tokenize_instr_format(self.format)
        if len(format_tokens) != len(line.tokens)-1:
            # number of tokens in line should match number of format tokens
            return None

        values = {
            'rd': None,
            'rs': None,
            'rt': None,
            'immediate': None
        }
        for fmt_token, instr_token in zip(format_tokens, line.tokens[1:]):
            if not fmt_token.value in values:
                # fmt_token signifies a parenthesis or potential
                # other non-value token, raise error if fmt_token != instr_token
                if fmt_token.value != instr_token.value:
                    raise AssemblerError(
                        filename=line.filename,
                        linenum=line.linenum,
                        charnum=instr_token.charnum,
                        message='Invalid Syntax')

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
                    imm = line.program.get_local_symbols(line).get(instr_token.value)
                    if imm is None:
                        imm = line.program.global_symbols.get(instr_token.value)
                        if imm is None:
                            # Symbol does not exist
                            raise AssemblerError(
                                filename=line.filename,
                                linenum=line.linenum,
                                charnum=instr_token.charnum,
                                message='Label was never declared/defined in this scope')
                    if self.type == InstructionType.J_SHIFT_TYPE:
                        # For J-Shift Types, imm is the address of label >> 2
                        imm = imm >> 2
                    elif self.type == InstructionType.B_TYPE:
                        # For B-Types, imm is the signed offset between the target address
                        # and the next instruction's address
                        imm = c_uint32((imm - line.memory_addr - 4) >> 2).value
                elif instr_token.type == TokenType.IMMEDIATE:
                    # Instruction token is an immediate, get the value
                    imm = instr_token.value
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
            else:
                values[fmt_token.value] = instr_token.value

        res = self.encoding.format(rd=values['rd'], rt=values['rt'], rs=values['rs'],
                                   imm=values['immediate'])
        if bstring: return res
        return int(res, 2)

    def get_encoding_imm_size(self):
        bit_length = 0
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


def get_instructions():
    """
    Returns a list of all instructions
    """
    output = []

    output.append(
        Instruction('add rd, rs, rt', '000000{rs:05b}{rt:05b}{rd:05b}00000100000',
                    'Add 32 bit integers (trap on overflow): GPR[rd] = GPR[rs] + GPR[rt]',
                    InstructionType.R_TYPE))
    output.append(
        Instruction('addu rd, rs, rt', '000000{rs:05b}{rt:05b}{rd:05b}00000100001',
                    'Add 32 bit integers: GPR[rd] = GPR[rs] + GPR[rt]',
                    InstructionType.R_TYPE))
    output.append(
        Instruction('align rd, rs, rt, immediate', '011111{rs:05b}{rt:05b}{rd:05b}010{imm:02b}100000',
                    'Concatenate two GPRs and extract a contiguous subset at a byte position: '
                    'GPR[rd] = (GPR[rt] << (8*bp)) OR (GPR[rs] >> (32-8*bp))',
                    InstructionType.R_TYPE))
    output.append(
        Instruction('and rd, rs, rt', '000000{rs:05b}{rt:05b}{rd:05b}00000100100',
                    'Bitwise logical AND: GPR[rd] = GPR[rs] AND GPR[rt]',
                    InstructionType.R_TYPE))
    output.append(
        Instruction('bitswap rd, rt', '01111100000{rt:05b}{rd:05b}00000100000',
                    'Reverse bits in each byte: GPR[rd].byte(i) = reverse_bits(GPR[rt].byte(i)) for all bytes i',
                    InstructionType.R_TYPE))
    output.append(
        Instruction('break', '00000000000000000000000000001101',
                    'Case a breakpoint exception', InstructionType.R_TYPE))
    output.append(
        Instruction('clo rd, rs', '000000{rs:05b}00000{rd:05b}00001010001',
                    'Count Leading Ones in Word: GPR[rd] = count_leading_ones(GPR[rs])',
                    InstructionType.R_TYPE))
    output.append(
        Instruction('clz rd, rs', '000000{rs:05b}00000{rd:05b}00001010000',
                    'Count Leading Zeroes in Word: GPR[rd] = count_leading_zeroes(GPR[rs])',
                    InstructionType.R_TYPE))
    output.append(
        Instruction('div rd, rs, rt', '000000{rs:05b}{rt:05b}{rd:05b}00010011010',
                    'Divide 32 bit integers and save quotient (Signed): GPR[rd] = GPR[rs] // GPR[rt]',
                    InstructionType.R_TYPE))
    output.append(
        Instruction('divu rd, rs, rt', '000000{rs:05b}{rt:05b}{rd:05b}00010011011',
                    'Divide 32 bit integers and save quotient: GPR[rd] = GPR[rs] // GPR[rt]',
                    InstructionType.R_TYPE))
    output.append(
        Instruction('jalr rd, rs', '000000{rs:05b}00000{rd:05b}00000001001',
                    'Jump and Link Register: GPR[rd] = PC+4, PC = GPR[rs]',
                    InstructionType.R_TYPE))
    output.append(
        Instruction('mfc0 rt, rd, sel', '01000000000{rt:05b}{rd:05b}00000000{imm:03b}',
                    'Move from Coprocessor 0: GPR[rt] = CPR[0, rd, sel]',
                    InstructionType.R_TYPE))
    output.append(
        Instruction('mtc0 rt, rd, sel', '01000000100{rt:05b}{rd:05b}00000000{imm:03b}',
                    'Move to Coprocessor 0: CPR[0, rd, sel] = GPR[rt]',
                    InstructionType.R_TYPE))
    output.append(
        Instruction('mod rd, rs, rt', '000000{rs:05b}{rt:05b}{rd:05b}00011011010',
                    'Divide 32 bit integers and save remainder (Signed): GPR[rd] = GPR[rs] \\% GPR[rt]',
                    InstructionType.R_TYPE))
    output.append(
        Instruction('modu rd, rs, rt', '000000{rs:05b}{rt:05b}{rd:05b}00011011011',
                    'Divide 32 bit integers and save remainder: GPR[rd] = GPR[rs] \\% GPR[rt]',
                    InstructionType.R_TYPE))
    output.append(
        Instruction('muh rd, rs, rt', '000000{rs:05b}{rt:05b}{rd:05b}00011011000',
                    'Multiply 32 bit integers and save low word (Signed): GPR[rd] = GPR[rs] * GPR[rt]',
                    InstructionType.R_TYPE))
    output.append(
        Instruction('muhu rd, rs, rt', '000000{rs:05b}{rt:05b}{rd:05b}00011011001',
                    'Multiply 32 bit integers and save low word: GPR[rd] = GPR[rs] * GPR[rt]',
                    InstructionType.R_TYPE))
    output.append(
        Instruction('mul rd, rs, rt', '000000{rs:05b}{rt:05b}{rd:05b}00010011000',
                    'Multiply 32 bit integers and save high word (Signed): GPR[rd] = GPR[rs] * GPR[rt]',
                    InstructionType.R_TYPE))
    output.append(
        Instruction('mulu rd, rs, rt', '000000{rs:05b}{rt:05b}{rd:05b}00010011001',
                    'Multiply 32 bit integers and save high word: GPR[rd] = GPR[rs] * GPR[rt]',
                    InstructionType.R_TYPE))
    output.append(
        Instruction('nor rd, rs, rt', '000000{rs:05b}{rt:05b}{rd:05b}00000100111',
                    'Bitwise logical NOT OR: GPR[rd] = GPR[rs] NOR GPR[rt]',
                    InstructionType.R_TYPE))
    output.append(
        Instruction('or rd, rs, rt', '000000{rs:05b}{rt:05b}{rd:05b}00000100101',
                    'Bitwise logical OR: GPR[rd] = GPR[rs] OR GPR[rt]',
                    InstructionType.R_TYPE))
    output.append(
        Instruction('sll rt, rd, immediate', '00000000000{rt:05b}{rd:05b}{imm:05b}000000',
                    'Shift Left Logical with immediate: GPR[rd] = GPR[rt] << immediate',
                    InstructionType.R_TYPE))
    output.append(
        Instruction('sllv rd, rt, rs', '000000{rs:05b}{rt:05b}{rd:05b}00000000100',
                    'Shift Left Logical Variable: GPR[rd] = GPR[rt] << GPR[rs]',
                    InstructionType.R_TYPE))
    output.append(
        Instruction('slt rd, rt, rs', '000000{rs:05b}{rt:05b}{rd:05b}00000101010',
                    'Set on Less Than (Signed): GPR[rd] = GPR[rs] < GPR[rt]',
                    InstructionType.R_TYPE))
    output.append(
        Instruction('sra rd, rt, immediate', '00000000000{rt:05b}{rd:05b}{imm:05b}000011',
                    'Shift Right Arithmetic (duplicate sign-bit): GPR[rd] = GPR[rt] >> immediate',
                    InstructionType.R_TYPE))
    output.append(
        Instruction('sltu rd, rt, rs', '000000{rs:05b}{rt:05b}{rd:05b}00000101011',
                    'Set on Less Than: GPR[rd] = GPR[rs] < GPR[rt]',
                    InstructionType.R_TYPE))
    output.append(
        Instruction('srav rd, rt, rs', '000000{rs:05b}{rt:05b}{rd:05b}00000000111',
                    'Shift Right Arithmetic Variable (duplicate sign-bit): GPR[rd] = GPR[rt] >> GPR[rs]',
                    InstructionType.R_TYPE))
    output.append(
        Instruction('srl rd, rt, immediate', '00000000000{rt:05b}{rd:05b}{imm:05b}000010',
                    'Shift Right Arithmetic (insert zeroes): GPR[rd] = GPR[rt] >> immediate',
                    InstructionType.R_TYPE))
    output.append(
        Instruction('srlv rd, rt, rs', '000000{rs:05b}{rt:05b}{rd:05b}00000000110',
                    'Shift Right Logical Variable (insert zeroes): GPR[rd] = GPR[rt] >> GPR[rs]',
                    InstructionType.R_TYPE))
    output.append(
        Instruction('sub rd, rs, rt', '000000{rs:05b}{rt:05b}{rd:05b}00000100010',
                    'Subtraction (trap on overflow): GPR[rd] = GPR[rs] - GPR[rt]',
                    InstructionType.R_TYPE))
    output.append(
        Instruction('subu rd, rs, rt', '000000{rs:05b}{rt:05b}{rd:05b}00000100011',
                    'Subtraction: GPR[rd] = GPR[rs] - GPR[rt]',
                    InstructionType.R_TYPE))
    output.append(
        Instruction('syscall', '00000000000000000000000000001100',
                    'Cause a System Call exception', InstructionType.R_TYPE))
    output.append(
        Instruction('teq rs, rt', '000000{rs:05b}{rt:05b}0000000000110100',
                    'Trap if Equal: if GPR[rs] == GPR[rt], cause a trap exception',
                    InstructionType.R_TYPE))
    output.append(
        Instruction('tge rs, rt', '000000{rs:05b}{rt:05b}0000000000110000',
                    'Trap if Greater or Equal (Signed): if GPR[rs] >= GPR[rt], cause a trap exception',
                    InstructionType.R_TYPE))
    output.append(
        Instruction('tgeu rs, rt', '000000{rs:05b}{rt:05b}0000000000110001',
                    'Trap if Greater or Equal: if GPR[rs] >= GPR[rt], cause a trap exception',
                    InstructionType.R_TYPE))
    output.append(
        Instruction('tlt rs, rt', '000000{rs:05b}{rt:05b}0000000000110010',
                    'Trap if Less Than (Signed): if GPR[rs] < GPR[rt], cause a trap exception',
                    InstructionType.R_TYPE))
    output.append(
        Instruction('tltu rs, rt', '000000{rs:05b}{rt:05b}0000000000110011',
                    'Trap if Less Than: if GPR[rs] < GPR[rt], cause a trap exception',
                    InstructionType.R_TYPE))
    output.append(
        Instruction('tne rs, rt', '000000{rs:05b}{rt:05b}0000000000110110',
                    'Trap if Not Equal: if GPR[rs] != GPR[rt], cause a trap exception',
                    InstructionType.R_TYPE))
    output.append(
        Instruction('xor rd, rs, rt', '000000{rs:05b}{rt:05b}{rd:05b}00000100110',
                    'Bitwise XOR: GPR[rd] = GPR[rs] XOR GPR[rt]',
                    InstructionType.R_TYPE))

    output.append(
        Instruction('addiu rt, rs, immediate', '001001{rs:05b}{rt:05b}{imm:016b}',
                    'Addition with immediate (Unsigned): GPR[rt] = GPR[rs] + immediate',
                    InstructionType.I_TYPE))
    output.append(
        Instruction('addiupc rs, immediate', '111011{rs:05b}00{imm:019b}',
                    'Addition with immediate and PC: GPR[rs] = PC + (immediate << 2)',
                    InstructionType.I_TYPE))
    output.append(
        Instruction('aluipc rs, immediate', '111011{rs:05b}11111{imm:016b}',
                    'Aligned Addition with upper immediate and PC: GPR[rs] = 0x0FFFF AND (PC + (immediate << 16))',
                    InstructionType.I_TYPE))
    output.append(
        Instruction('andi rt, rs, immediate', '001100{rs:05b}{rt:05b}{imm:016b}',
                    'Bitwise AND with immediate: GPR[rt] = GPR[rs] AND zero_extend(immediate)',
                    InstructionType.I_TYPE))
    output.append(
        Instruction('aui rt, rs, immediate', '001111{rs:05b}{rt:05b}{imm:016b}',
                    'Addition with immediate to upper bits: GPR[rt] = GPR[rs] + (immediate << 16)',
                    InstructionType.I_TYPE))
    output.append(
        Instruction('auipc rs, immediate', '111011{rs:05b}11110{imm:016b}',
                    'Addition with upper immediate to PC: GPR[rs] = PC + (immediate << 16)',
                    InstructionType.I_TYPE))
    output.append(
        Instruction('lb rt, immediate(rs)', '100000{rs:05b}{rt:05b}{imm:016b}',
                    'Load Byte from memory as signed value: GPR[rt] = MEM[GPR[rs] + immediate]',
                    InstructionType.I_TYPE))
    output.append(
        Instruction('lbu rt, immediate(rs)', '100100{rs:05b}{rt:05b}{imm:016b}',
                    'Load Byte from memory as unsigned value: GPR[rt] = MEM[GPR[rs] + immediate]',
                    InstructionType.I_TYPE))
    output.append(
        Instruction('lh rt, immediate(rs)', '100001{rs:05b}{rt:05b}{imm:016b}',
                    'Load Halfword from memory as signed value: GPR[rt] = MEM[GPR[rs] + immediate]',
                    InstructionType.I_TYPE))
    output.append(
        Instruction('lhu rt, immediate(rs)', '100101{rs:05b}{rt:05b}{imm:016b}',
                    'Load Halfword from memory as unsigned value: GPR[rt] = MEM[GPR[rs] + immediate]',
                    InstructionType.I_TYPE))
    output.append(
        Instruction('lw rt, immediate(rs)', '100011{rs:05b}{rt:05b}{imm:016b}',
                    'Load Word from memory as signed value: GPR[rt] = MEM[GPR[rs] + immediate]',
                    InstructionType.I_TYPE))
    output.append(
        Instruction('lwpc rs, immediate', '111011{rs:05b}01{imm:019b}',
                    'Load Word from memory as signed value using PC-relative address: GPR[rs] = MEM[PC + (immediate << 2)]',
                    InstructionType.I_TYPE))
    output.append(
        Instruction('ori rt, rs, immediate', '001101{rs:05b}{rt:05b}{imm:016b}',
                    'Bitwise OR with immediate: GPR[rt] = GPR[rs] OR zero_extend(immediate)',
                    InstructionType.I_TYPE))
    output.append(
        Instruction('sb rt, immediate(rs)', '101000{rs:05b}{rt:05b}{imm:016b}',
                    'Store Byte in memory: MEM[GPR[rs] + immediate] = GPR[rt]',
                    InstructionType.I_TYPE))
    output.append(
        Instruction('sh rt, immediate(rs)', '101001{rs:05b}{rt:05b}{imm:016b}',
                    'Store Halfword in memory: MEM[GPR[rs] + immediate] = GPR[rt]',
                    InstructionType.I_TYPE))
    output.append(
        Instruction('slti rt, rs, immediate', '001010{rs:05b}{rt:05b}{imm:016b}',
                    'Set on Less Than Immediate (Signed): GPR[rt] = GPR[rs] < sign_extend(immediate)',
                    InstructionType.I_TYPE))
    output.append(
        Instruction('slti rt, rs, immediate', '001011{rs:05b}{rt:05b}{imm:016b}',
                    'Set on Less Than Immediate (Unsigned): GPR[rt] = GPR[rs] < sign_extend(immediate)',
                    InstructionType.I_TYPE))
    output.append(
        Instruction('sw rt, immediate(rs)', '101011{rs:05b}{rt:05b}{imm:016b}',
                    'Store Word in memory: MEM[GPR[rs] + immediate] = GPR[rt]',
                    InstructionType.I_TYPE))
    output.append(
        Instruction('xori rt, rs, immediate', '001110{rs:05b}{rt:05b}{imm:016b}',
                    'Bitwise Exclusive OR with Immediate: GPR[rt] = GPR[rs] XOR immediate',
                    InstructionType.I_TYPE))

    output.append(
        Instruction('bal immediate', '0000010000010001{imm:016b}',
                    'Branch and Link: GPR[31] = PC+4, PC = (immediate << 2) + PC + 4',
                    InstructionType.B_TYPE))
    output.append(
        Instruction('balc immediate', '111010{imm:026b}',
                    'Branch and Link Compact: GPR[31] = PC+4, PC = (immediate << 2) + PC + 4',
                    InstructionType.B_TYPE))
    output.append(
        Instruction('bc immediate', '110010{imm:026b}',
                    'Branch Compact: PC = (immediate << 2) + PC + 4',
                    InstructionType.B_TYPE))
    output.append(
        Instruction('beq rs, rt, immediate', '000100{rs:05b}{rt:05b}{imm:016b}',
                    'Branch on Equal: if GPR[rs] == GPR[rt], PC = (immediate << 2) + PC + 4',
                    InstructionType.B_TYPE))
    output.append(
        Instruction('bgez rs, immediate', '000001{rs:05b}00001{imm:016b}',
                    'Branch on Greater Than or Equal to Zero: if GPR[rs] >= 0, branch',
                    InstructionType.B_TYPE))
    output.append(
        Instruction('bgtz rs, immediate', '000111{rs:05b}00000{imm:016b}',
                    'Branch on Greater Than Zero: if GPR[rs] > 0, branch',
                    InstructionType.B_TYPE))
    output.append(
        Instruction('blez rs, immediate', '000110{rs:05b}00000{imm:016b}',
                    'Branch on Less Than or Equal to Zero: if GPR[rs] <= 0, branch',
                    InstructionType.B_TYPE))
    output.append(
        Instruction('bltz rs, immediate', '000001{rs:05b}00000{imm:016b}',
                    'Branch on Less than Zero: if GPR[rs] < 0, branch',
                    InstructionType.B_TYPE))
    output.append(
        Instruction('bne rs, rt, immediate', '000101{rs:05b}{rt:05b}{imm:016b}',
                    'Branch on Not Equal: if GPR[rs] != GPR[rt], branch',
                    InstructionType.B_TYPE))
    output.append(
        Instruction('blezalc rt, immediate', '00011000000{rt:05b}{imm:016b}',
                    'Branch Less Than or Equal to Zero And Link: Compact branch-and-link if GPR[rt] <= 0',
                    InstructionType.B_TYPE))
    output.append(
        Instruction('bgezalc rt, immediate', '000110{rt:05b}{rt:05b}{imm:016b}',
                    'Branch Greater Than or Equal to Zero And Link: Compact branch-and-link if GPR[rt] >= 0',
                    InstructionType.B_TYPE, comp_regs=True, reg1_zero=False, reg2_zero=False))
    output.append(
        Instruction('bgtzalc rt, immediate', '00011100000{rt:05b}{imm:016b}',
                    'Branch Greater Than Zero And Link: Compact branch-and-link if GPR[rt] > 0',
                    InstructionType.B_TYPE))
    output.append(
        Instruction('bltzalc rt, immediate', '000111{rt:05b}{rt:05b}{imm:016b}',
                    'Branch Less Than Zero And Link: Compact branch-and-link if GPR[rt] < 0',
                    InstructionType.B_TYPE, comp_regs=True, reg1_zero=False, reg2_zero=False))
    output.append(
        Instruction('beqzalc rt, immediate', '00100000000{rt:05b}{imm:016b}',
                    'Branch if Equal to Zero And Link: Compact branch-and-link if GPR[rt] == 0',
                    InstructionType.B_TYPE))
    output.append(
        Instruction('bnezalc rt, immediate', '01100000000{rt:05b}{imm:016b}',
                    'Branch if Not Equal to Zero And Link: Compact branch-and-link if GPR[rt] != 0',
                    InstructionType.B_TYPE))
    output.append(
        Instruction('bltc rs, rt, immediate', '010111{rs:05b}{rt:05b}{imm:016b}',
                    'Branch if Less Than Compact (Signed): if GPR[rs] < GPR[rt], branch',
                    InstructionType.B_TYPE, comp_regs=False, reg1_zero=False, reg2_zero=False))
    output.append(
        Instruction('bltuc rs, rt, immediate', '000111{rs:05b}{rt:05b}{imm:016b}',
                    'Branch if Less Than Compact (Unsigned): if GPR[rs] < GPR[rt], branch',
                    InstructionType.B_TYPE, comp_regs=False, reg1_zero=False, reg2_zero=False))
    output.append(
        Instruction('bgec rs, rt, immediate', '010110{rs:05b}{rt:05b}{imm:016b}',
                    'Branch if Greater Than or Equal Compact (Signed): if GPR[rs] >= GPR[rt], branch',
                    InstructionType.B_TYPE, comp_regs=False, reg1_zero=False, reg2_zero=False))
    output.append(
        Instruction('bgeuc rs, rt, immediate', '000110{rs:05b}{rt:05b}{imm:016b}',
                    'Branch if Greater Than or Equal Compact (Unsigned): if GPR[rs] >= GPR[rt], branch',
                    InstructionType.B_TYPE, comp_regs=False, reg1_zero=False, reg2_zero=False))
    output.append(
        Instruction('bltzc rt, immediate', '010111{rt:05b}{rt:05b}{imm:016b}',
                    'Branch if Less Than Zero Compact: if GPR[rt] < 0, branch',
                    InstructionType.B_TYPE, comp_regs=True, reg1_zero=False, reg2_zero=False))
    output.append(
        Instruction('blezc rt, immediate', '01011000000{rt:05b}{imm:016b}',
                    'Branch if Less Than or Equal to Zero Compact: if GPR[rt] <= 0, branch',
                    InstructionType.B_TYPE, comp_regs=False, reg2_zero=False))
    output.append(
        Instruction('bgezc rt, immediate', '010110{rt:05b}{rt:05b}{imm:016b}',
                    'Branch if Greater Than or Equal to Zero Compact: if GPR[rt] >= 0, branch',
                    InstructionType.B_TYPE, comp_regs=True))
    output.append(
        Instruction('bgtzc rt, immediate', '01011100000{rt:05b}{imm:016b}',
                    'Branch if Greater Than Zero Compact: if GPR[rt] > 0, branch',
                    InstructionType.B_TYPE, comp_regs=False))
    output.append(
        Instruction('beqzc rs, immediate', '110110{rs:05b}{imm:021b}',
                    'Branch if Equal to Zero Compact: if GPR[rt] == 0, branch',
                    InstructionType.B_TYPE, reg1_zero=False))
    output.append(
        Instruction('bnezc rs, immediate', '111110{rs:05b}{imm:021b}',
                    'Branch if Not Equal to Zero Compact: if GPR[rt] != 0, branch',
                    InstructionType.B_TYPE, reg1_zero=False))
    output.append(
        Instruction('bovc rs, rt, immediate', '001000{rs:05b}{rt:05b}{imm:016b}',
                    'Branch on Overflow Compact: if GPR[rs] + GPR[rt] causes overflow, branch',
                    InstructionType.B_TYPE))
    output.append(
        Instruction('bnvc rs, rt, immediate', '011000{rs:05b}{rt:05b}{imm:016b}',
                    'Branch on No Overflow Compact: if GPR[rs] + GPR[rt] causes no overflow, branch',
                    InstructionType.B_TYPE))

    output.append(
        Instruction('j immediate', '000010{imm:026b}',
                    'Jump to immediate address', InstructionType.J_SHIFT_TYPE))
    output.append(
        Instruction('jal immediate', '000011{imm:026b}',
                    'Jump and Link to immediate address: Store next address in GPR[31]',
                    InstructionType.J_SHIFT_TYPE))
    output.append(
        Instruction('jialc rt, immediate', '11111000000{rt:05b}{imm:016b}',
                    'Jump Indexed and Link Compact: Store next address in GPR[31] and jump to (immediate + GPR[rt])',
                    InstructionType.J_TYPE))
    output.append(
        Instruction('jic rt, immediate', '11011000000{rt:05b}{imm:016b}',
                    'Jump Indexed Compact: Jump to (immediate + GPR[rt])',
                    InstructionType.J_TYPE))
    return output