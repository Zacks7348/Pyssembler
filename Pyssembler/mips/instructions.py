from Pyssembler.simulator.errors import InvalidRegisterError
from .hardware import RF, MEM, CP0, GP_REGS, CP0_REGS
from .utils import Integer

import sys
import inspect
from typing import Union


def setup_instructions():
    """
    Returns a dict of all instruction objects declared in this file
    """
    instructions = {}
    exclude = ['Instruction', 'RTypeInstruction']
    for name, obj in inspect.getmembers(sys.modules[__name__]):
        if inspect.isclass(obj) and not name in exclude and issubclass(obj, Instruction):
            instructions[name.lower()] = obj()
    return instructions


class Instruction:
    """
    Base class for supported mips instructions
    """

    def __init__(self, mnemonic, op, encoding, instr_format, description) -> None:
        self.mnemonic = mnemonic
        self.op = op
        self.encoding = encoding
        self.format = instr_format
        self.description = description

    def __str__(self) -> str:
        return 'MIPS32 INSTRUCTION: '+self.mnemonic

    def __repr__(self) -> str:
        return 'MIPS32 INSTRUCTION: mnemonic={}, formatting={}, encoding={}'.format(self.mnemonic, self.format, self.encoding)


class RTypeInstruction(Instruction):
    """
    Base class for all R-type instructions

    This inherits from `Instruction`
    """

    def __init__(self, mnemonic, op, func, encoding, instr_format, description) -> None:
        super().__init__(mnemonic, op, encoding, instr_format, description)
        self.func = func

    def match(self, instr: int):
        """
        Check if passed instruction's op and func codes are the same as ours. 

        Generic check for R-Type instructions
        """
        return self.op == Integer.get_bits(instr, 26, 31) and self.func == Integer.get_bits(instr, 0, 5)

    def encode(self, instr: str) -> Union[str, tuple]:
        """
        Generic function to encode a R-Type instruction (3 register instruction).

        If something went wrong, return error and what caused it. Up to caller
        to handle error 
        """
        tokens = instr.split()
        if tokens[0] != self.mnemonic:
            # instr is not us
            raise ValueError('Cannot encode {} as {}'.format(instr, self))
        rd = _encode_register(tokens[1])
        if rd is None:
            return InvalidRegisterError, tokens[1]
        rs = _encode_register(tokens[2])
        if rs is None:
            return InvalidRegisterError, tokens[2]
        rt = _encode_register(tokens[3])
        if rt is None:
            return InvalidRegisterError, tokens[3]
        return self.encoding.format(rd=rd, rs=rs, rt=rt)


class Add(RTypeInstruction):
    """
    MIPS32 ADD instruction
    """

    def __init__(self) -> None:
        super().__init__('add', 0b000000, 0b100000, '000000{rs}{rt}{rd}00000100000',
                         'add rd, rs, rt',
                         'Addition (trap on overflow): GPR[rd] = GPR[rs] + GPR[rt]')


class Addu(RTypeInstruction):
    """
    MIPS32 ADDU instruction
    """

    def __init__(self) -> None:
        super().__init__('addu', 0b000000, 0b100001, '000000{rs}{rt}{rd}00000100001',
                         'addu rd, rs, rt',
                         'Addition: GPR[rd] = GPR[rs] + GPR[rt]')


class And(RTypeInstruction):
    """
    MIPS32 AND instruction
    """

    def __init__(self) -> None:
        super().__init__('and', 0b000000, 0b100100, '000000{rs}{rt}{rd}00000100100',
                         'and rd, rs, rt',
                         'Bitwise AND: GPR[rd] = GPR[rs] AND GPR[rt]')


class Nor(RTypeInstruction):
    """
    MIPS32 NOR instruction
    """

    def __init__(self) -> None:
        super().__init__('nor', 0b000000, 0b100111, '000000{rs}{rt}{rd}00000100111',
                         'nor rd, rs, rt',
                         'Bitwise NOT OR: GPR[rd] = GPR[rs] NOT OR GPR[rt]')


class Or(RTypeInstruction):
    """
    MIPS32 OR instruction
    """

    def __init__(self) -> None:
        super().__init__('or', 0b000000, 0b100101, '000000{rs}{rt}{rd}00000100101',
                         'or rd, rs, rt',
                         'Bitwise OR: GPR[rd] = GPR[rs] OR GPR[rt]')


class Slt(RTypeInstruction):
    """
    MIPS32 SLT instruction
    """

    def __init__(self) -> None:
        super().__init__('slt', 0b000000, 0b101010, '000000{rs}{rt}{rd}00000101010',
                         'slt rd, rs, rt',
                         'Set on Less Than: GPR[rd] = GPR[rs] < GPR[rt]')


class Sltu(RTypeInstruction):
    """
    MIPS32 SLTU instruction
    """

    def __init__(self) -> None:
        super().__init__('sltu', 0b000000, 0b101011, '000000{rs}{rt}{rd}00000101011',
                         'sltu rd, rs, rt',
                         'Set on Less Than (unsigned): GPR[rd] = GPR[rs] < GPR[rt]')


class Sub(RTypeInstruction):
    """
    MIPS32 SUB instruction
    """

    def __init__(self) -> None:
        super().__init__('sub', 0b000000, 0b100010, '000000{rs}{rt}{rd}00000100010',
                         'sub rd, rs, rt',
                         'Subtraction (trap on overflow): GPR[rd] = GPR[rs] - GPR[rt]')


class Subu(RTypeInstruction):
    """
    MIPS32 SUBU instruction
    """

    def __init__(self) -> None:
        super().__init__('subu', 0b000000, 0b100011, '000000{rs}{rt}{rd}00000100011',
                         'subu rd, rs, rt',
                         'Subtraction: GPR[rd] = GPR[rs] - GPR[rt]')


class Xor(RTypeInstruction):
    """
    MIPS32 XOR instruction
    """

    def __init__(self) -> None:
        super().__init__('xor', 0b000000, 0b100110, '000000{rs}{rt}{rd}00000100110',
                         'xor rd, rs, rt',
                         'Bitwise XOR: GPR[rd] = GPR[rs] XOR GPR[rt]')


class Mul(RTypeInstruction):
    """
    MIPS32 MUL instruction
    """

    def __init__(self) -> None:
        super().__init__('mul', 0b000000, 0b011000, '000000{rs}{rt}{rd}00010011000',
                         'mul rd, rs, rt',
                         'Multiplication: GPR[rd] = lo_word(GPR[rs] * GPR[rt])')


class Muh(RTypeInstruction):
    """
    MIPS32 MUH instruction
    """

    def __init__(self) -> None:
        super().__init__('muh', 0b000000, 0b011000, '000000{rs}{rt}{rd}00011011000',
                         'muh rd, rs, rt',
                         'Multiplication: GPR[rd] = hi_word(GPR[rs] * GPR[rt])')


class Mulu(RTypeInstruction):
    """
    MIPS32 MULU instruction
    """

    def __init__(self) -> None:
        super().__init__('mulu', 0b000000, 0b011001, '000000{rs}{rt}{rd}00010011001',
                         'mulu rd, rs, rt',
                         'Multiplication (unsigned): GPR[rd] = lo_word(GPR[rs] * GPR[rt])')


class Muhu(RTypeInstruction):
    """
    MIPS32 MUHU instruction
    """

    def __init__(self) -> None:
        super().__init__('muh', 0b000000, 0b011001, '000000{rs}{rt}{rd}00011011001',
                         'muhu rd, rs, rt',
                         'Multiplication (unsigned): GPR[rd] = hi_word(GPR[rs] * GPR[rt])')


class Div(RTypeInstruction):
    """
    MIPS32 DIV instruction
    """

    def __init__(self) -> None:
        super().__init__('div', 0b000000, 0b011010, '000000{rs}{rt}{rd}00010011010',
                         'div rd, rs, rt',
                         'Integer Division: GPR[rd] = GPR[rs] / GPR[rt]')


class Mod(RTypeInstruction):
    """
    MIPS32 MOD instruction
    """

    def __init__(self) -> None:
        super().__init__('mod', 0b000000, 0b011010, '000000{rs}{rt}{rd}00011011010',
                         'mod rd, rs, rt',
                         'Modulo: GPR[rd] = GPR[rs] \\% GPR[rt]')


class Divu(RTypeInstruction):
    """
    MIPS32 DIVU instruction
    """

    def __init__(self) -> None:
        super().__init__('divu', 0b000000, 0b011011, '000000{rs}{rt}{rd}00010011011',
                         'divu rd, rs, rt',
                         'Integer Division (unsigned): GPR[rd] = GPR[rs] / GPR[rt]')


class Modu(RTypeInstruction):
    """
    MIPS32 MODU instruction
    """

    def __init__(self) -> None:
        super().__init__('modu', 0b000000, 0b011011, '000000{rs}{rt}{rd}00011011011',
                         'modu rd, rs, rt',
                         'Modulo (unsigned): GPR[rd] = GPR[rs] \\% GPR[rt]')


class Clo(RTypeInstruction):
    """
    MIPS32 CLO instruction
    """

    def __init__(self) -> None:
        super().__init__('clo', 0b000000, 0b010001, '000000{rs}00000{rd}00001010001',
                         'clo rd, rs, rt',
                         'Count Leading Ones: GPR[rd] = count_leading_ones(GPR[rs])')


class Clz(RTypeInstruction):
    """
    MIPS32 CLZ instruction
    """

    def __init__(self) -> None:
        super().__init__('clz', 0b000000, 0b010000, '000000{rs}00000{rd}00001010000',
                         'clz rd, rs, rt',
                         'Count Leading Zeroes: GPR[rd] = count_leading_zeroes(GPR[rs])')


class Sll(RTypeInstruction):
    """
    MIPS32 SLL instruction
    """

    def __init__(self) -> None:
        super().__init__('sll', 0b000000, 0b000000, '00000000000{rt}{rd}{sa}000000',
                         'sll rd, rt, sa',
                         'Shift Left Logical: GPR[rd] = GPR[rt] << sa')


class Sra(RTypeInstruction):
    """
    MIPS32 SRA instruction
    """

    def __init__(self) -> None:
        super().__init__('sra', 0b000000, 0b000011, '00000000000{rt}{rd}{sa}000011',
                         'sra rd, rt, sa',
                         'Shift Right Arithmetic: GPR[rd] = GPR[rt] >> sa')


class Srl(RTypeInstruction):
    """
    MIPS32 SRL instruction
    """

    def __init__(self) -> None:
        super().__init__('srl', 0b000000, 0b000010, '00000000000{rt}{rd}{sa}000010',
                         'srl rd, rt, sa',
                         'Shift Right Logical: GPR[rd] = GPR[rt] >> sa')


class Sllv(RTypeInstruction):
    """
    MIPS32 SLLV instruction
    """

    def __init__(self) -> None:
        super().__init__('sllv', 0b000000, 0b000100, '000000{rs}{rt}{rd}00000000100',
                         'sllv rd, rt, rs',
                         'Shift Left Logical Variable: GPR[rd] = GPR[rt] << GPR[rs]')


class Srav(RTypeInstruction):
    """
    MIPS32 SRAV instruction
    """

    def __init__(self) -> None:
        super().__init__('srav', 0b000000, 0b000111, '000000{rs}{rt}{rd}00000000111',
                         'srav rd, rt, rs',
                         'Shift Right Arithmetic Variable: GPR[rd] = GPR[rt] >> GPR[rs]')


class Srlv(RTypeInstruction):
    """
    MIPS32 SRLV instruction
    """

    def __init__(self) -> None:
        super().__init__('srlv', 0b000000, 0b000110, '000000{rs}{rt}{rd}00000000110',
                         'srlv rd, rt, rs',
                         'Shift Right Logical Variable: GPR[rd] = GPR[rt] >> GPR[rs]')


class Jalr(RTypeInstruction):
    """
    MIPS32 JALR instruction
    """

    def __init__(self) -> None:
        super().__init__('jalr', 0b000000, 0b001001, '000000{rs}000001111000000001001',
                         'jalr rs',
                         'Jump and Link Reg: GPR[31] = return_addr, PC = GPR[rs]')


class Mfc0(RTypeInstruction):
    """
    MIPS32 MFC0 instruction
    """

    def __init__(self) -> None:
        super().__init__('mfc0', 0b010000, 0b000000, '01000000000{rt}{rd}00000000000',
                         'mfc0 rt, rd',
                         'Move From Coprocessor 0: GPR[rt] = CPR[0, rd]')


class Mtc0(RTypeInstruction):
    """
    MIPS32 MTC0 instruction
    """

    def __init__(self) -> None:
        super().__init__('mtc0', 0b010000, 0b000000, '01000000100{rt}{rd}00000000000',
                         'mtc0 rt, rd',
                         'Move From Coprocessor 0: CPR[0, rd] = GPR[rt]')


class Syscall(RTypeInstruction):
    """
    MIPS32 SYSCALL instruction
    """

    def __init__(self) -> None:
        super().__init__('syscall', 0b000000, 0b001100, '00000000000000000000000000001100',
                         'syscall',
                         'System Call: Run syscall specified in $v0')


class Break(RTypeInstruction):
    """
    MIPS32 BREAK instruction
    """

    def __init__(self) -> None:
        super().__init__('break', 0b000000, 0b001101, '00000000000000000000000000001101',
                         'break',
                         'Break: Terminate program with exception')


class Nop(RTypeInstruction):
    """
    MIPS32 NOP instruction
    """

    def __init__(self) -> None:
        super().__init__('nop', 0b000000, 0b000000, '00000000000000000000000000000000',
                         'nop',
                         'NOP: Blank instruction. Executed as a sll instruction with all encodings set to 0s')


class Teq(RTypeInstruction):
    """
    MIPS32 TEQ instruction
    """

    def __init__(self) -> None:
        super().__init__('teq', 0b000000, 0b110100, '000000{rs}{rt}0000000000110100',
                         'teq rs, rt',
                         'Trap if Equal: Trap if GPR[rs] == GPR[rt]')


class Tge(RTypeInstruction):
    """
    MIPS32 TGE instruction
    """

    def __init__(self) -> None:
        super().__init__('tge', 0b000000, 0b110000, '000000{rs}{rt}0000000000110000',
                         'tge rs, rt',
                         'Trap if Greater or Equal: Trap if GPR[rs] >= GPR[rt]')


class Tgeu(RTypeInstruction):
    """
    MIPS32 TGEU instruction
    """

    def __init__(self) -> None:
        super().__init__('tgeu', 0b000000, 0b110001, '000000{rs}{rt}0000000000110001',
                         'tgeu rs, rt',
                         'Trap if Greater or Equal (unsigned): Trap if GPR[rs] >= GPR[rt]')


class Tlt(RTypeInstruction):
    """
    MIPS32 TLT instruction
    """

    def __init__(self) -> None:
        super().__init__('tlt', 0b000000, 0b110010, '000000{rs}{rt}0000000000110010',
                         'tlt rs, rt',
                         'Trap if Less Than: Trap if GPR[rs] < GPR[rt]')


class Tltu(RTypeInstruction):
    """
    MIPS32 TLTU instruction
    """

    def __init__(self) -> None:
        super().__init__('tltu', 0b000000, 0b110011, '000000{rs}{rt}0000000000110011',
                         'tltu rs, rt',
                         'Trap if Less Than (unsigned): Trap if GPR[rs] < GPR[rt]')


class Tne(RTypeInstruction):
    """
    MIPS32 TNE instruction
    """

    def __init__(self) -> None:
        super().__init__('tne', 0b000000, 0b110110, '000000{rs}{rt}0000000000110110',
                         'tne rs, rt',
                         'Trap if Not Equal: Trap if GPR[rs] != GPR[rt]')

# class ITYPE_Instruction(Instruction):
#     """
#     Base class for all I-type instructions
#     """

#     def __init__(self, mnemonic, op, encoding, instr_format, description) -> None:
#         super().__init__(mnemonic, op, encoding, instr_format, description)


# class IBTYPE_Instruction(Instruction):
#     """
#     Base class for all I-B-type instructions
#     """

#     def __init__(self, mnemonic, op, encoding, instr_format, description) -> None:
#         super().__init__(mnemonic, op, encoding, instr_format, description)


# class JTYPE_Instruction(Instruction):
#     """
#     Base class for all J-type instructions
#     """

#     def __init__(self, mnemonic, op, encoding, instr_format, description) -> None:
#         super().__init__(mnemonic, op, encoding, instr_format, description)


def _encode_register(reg: str):
    """
    Helper function to encode a register
    Returns int addr of register or None if failed
    """
    reg = reg.replace(',', '')
    if reg in GP_REGS:
        return Integer.to_bin_string(GP_REGS[reg], bits=5)
    if reg in CP0_REGS:
        return Integer.to_bin_string(CP0_REGS[reg], bits=5)
    return None
