from pyssembler.mips.instructions.base_instruction import MIPSBasicInstruction, InstructionType


class AddInstruction(MIPSBasicInstruction):
    """
    Represents the ADD MIPS instruction 
    """

    def __init__(self):
        super().__init__(
            'add',
            'add rd, rs, rt',
            'Add 32 bit integers (trap on overflow)',
            '000000{rs:05b}{rt:05b}{rd:05b}00000100000',
            InstructionType.R_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'add'


class AddiuInstruction(MIPSBasicInstruction):
    """
    Represents the ADDIU MIPS instruction
    """

    def __init__(self):
        super().__init__(
            'addiu',
            'addiu rt, rs, immediate',
            'To add a constant to a 32-bit integer',
            '001001{rs:05b}{rt:05b}{imm:016b}',
            InstructionType.I_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'addiu'


class AddiupcInstruction(MIPSBasicInstruction):
    """
    Represents the ADDIUPC MIPS instruction
    """

    def __init__(self):
        super().__init__(
            'addiupc',
            'addiupc rs, immediate',
            'Add Immediate to PC (unsigned - non-trapping)',
            '111011{rs:05b}00{imm:019b}',
            InstructionType.I_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'addiupc'


class AdduInstruction(MIPSBasicInstruction):
    """
    Represents the ADDU MIPS instruction
    """

    def __init__(self):
        super().__init__(
            'addu',
            'addu rd, rs, rt',
            'To add 32-bit integers',
            '000000{rs:05b}{rt:05b}{rd:05b}00000100001',
            InstructionType.R_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'addu'


class AlignInstruction(MIPSBasicInstruction):
    """
    Represents the ALIGN MIPS instruction
    """

    def __init__(self):
        super().__init__(
            'align',
            'align rd, rs, rt, immediate',
            'Concatenate two GPRs and extract a contiguous subset at a byte position',
            '011111{rs:05b}{rt:05b}{rd:05b}010{imm:02b}100000',
            InstructionType.R_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'align'


class AluipcInstruction(MIPSBasicInstruction):
    """
    Represents the ALUIPC MIPS instruction
    """

    def __init__(self):
        super().__init__(
            'aluipc',
            'aluipc rs, immediate',
            'Aligned Addition with upper immediate and PC',
            '111011{rs:05b}11111{imm:016b}',
            InstructionType.I_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'aluipc'


class AndInstruction(MIPSBasicInstruction):
    """
    Represents the AND MIPS instruction
    """

    def __init__(self):
        super().__init__(
            'and',
            'and rd, rs, rt',
            'To do a bitwise logical AND',
            '000000{rs:05b}{rt:05b}{rd:05b}00000100100',
            InstructionType.R_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'and'


class AndiInstruction(MIPSBasicInstruction):
    """
    Represents the ANDI MIPS instruction
    """

    def __init__(self):
        super().__init__(
            'andi',
            'andi rt, rs, immediate',
            'To do a bitwise logical AND with an immediate',
            '001100{rs:05b}{rt:05b}{imm:016b}',
            InstructionType.I_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'andi'


class AuiInstruction(MIPSBasicInstruction):
    """
    Represents the AUI MIPS instruction
    """

    def __init__(self):
        super().__init__(
            'aui',
            'aui rt, rs, immediate',
            'Add upper immediate',
            '001111{rs:05b}{rt:05b}{imm:016b}',
            InstructionType.I_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'aui'


class AuipcInstruction(MIPSBasicInstruction):
    """
    Represents the AUIPC MIPS instruction
    """

    def __init__(self):
        super().__init__(
            'auipc',
            'auipc rs, immediate',
            'Add Upper Immediate to PC',
            '111011{rs:05b}11110{imm:016b}',
            InstructionType.I_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'auipc'


class BalcInstruction(MIPSBasicInstruction):
    """
    Represents the BALC MIPS instruction
    """

    def __init__(self):
        super().__init__(
            'balc',
            'balc immediate',
            'To do an unconditional PC-relative procedure call (no delay slot)',
            '111010{imm:026b}',
            InstructionType.B_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'balc'


class BcInstruction(MIPSBasicInstruction):
    """
    Represents the BC MIPS instruction
    """

    def __init__(self):
        super().__init__(
            'bc',
            'bc immediate',
            'Branch, Compact',
            '110010{imm:026b}',
            InstructionType.B_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'bc'


class BeqInstruction(MIPSBasicInstruction):
    """
    Represents the BEQ MIPS instruction
    """

    def __init__(self):
        super().__init__(
            'beq',
            'beq rs, rt, immediate',
            'To compare GPRs then do a PC-relative conditional branch',
            '000100{rs:05b}{rt:05b}{imm:016b}',
            InstructionType.B_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'beq'


class BeqcInstruction(MIPSBasicInstruction):
    """
    Represents the BEQC MIPS instruction
    """

    def __init__(self):
        super().__init__(
            'beqc',
            'beqc rs, rt, offset',
            'Equal register-register compare and branch with 16-bit offset',
            '001000{rs:05b}{rt:05b}{imm:016b}',
            InstructionType.B_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'beqc'


class BeqzalcInstruction(MIPSBasicInstruction):
    """
    Represents the BEQZALC MIPS instruction
    """

    def __init__(self):
        super().__init__(
            'beqzalc',
            'beqzalc rt, immediate',
            'Compact branch-and-link if GPR rt is equal to zero',
            '00100000000{rt:05b}{imm:016b}',
            InstructionType.B_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'beqzalc'


class BeqzcInstruction(MIPSBasicInstruction):
    """
    Represents the BEQZC MIPS instruction
    """

    def __init__(self):
        super().__init__(
            'beqzc',
            'beqzc rs, immediate',
            'Branch if Equal to Zero Compact',
            '110110{rs:05b}{imm:021b}',
            InstructionType.B_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'beqzc'


class BgecInstruction(MIPSBasicInstruction):
    """
    Represents the BGEC MIPS instruction
    """

    def __init__(self):
        super().__init__(
            'bgec',
            'bgec rs, rt, immediate',
            'Branch if Greater Than or Equal Compact (Signed)',
            '010110{rs:05b}{rt:05b}{imm:016b}',
            InstructionType.B_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'bgec'


class BgeucInstruction(MIPSBasicInstruction):
    """
    Represents the BGEUC MIPS instruction
    """

    def __init__(self):
        super().__init__(
            'bgeuc',
            'bgeuc rs, rt, immediate',
            'Branch if Greater Than or Equal Compact (Unsigned)',
            '000110{rs:05b}{rt:05b}{imm:016b}',
            InstructionType.B_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'bgeuc'


class BgezInstruction(MIPSBasicInstruction):
    """
    Represents the BGEZ MIPS instruction
    """

    def __init__(self):
        super().__init__(
            'bgez',
            'bgez rs, immediate',
            'Branch on Greater Than or Equal to Zero',
            '000001{rs:05b}00001{imm:016b}',
            InstructionType.B_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'bgez'


class BgezalcInstruction(MIPSBasicInstruction):
    """
    Represents the BGEZALC MIPS instruction
    """

    def __init__(self):
        super().__init__(
            'bgezalc',
            'bgezalc rt, immediate',
            'Compact branch-and-link if GPR rt is greater than or equal to zero',
            '000110{rt:05b}{rt:05b}{imm:016b}',
            InstructionType.B_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'bgezalc'


class BgezcInstruction(MIPSBasicInstruction):
    """
    Represents the BGEZC MIPS instruction
    """

    def __init__(self):
        super().__init__(
            'bgezc',
            'bgezc rt, immediate',
            'Branch if Greater Than or Equal to Zero Compact',
            '010110{rt:05b}{rt:05b}{imm:016b}',
            InstructionType.B_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'bgezc'


class BgtzInstruction(MIPSBasicInstruction):
    """
    Represents the BGTZ MIPS instruction
    """

    def __init__(self):
        super().__init__(
            'bgtz',
            'bgtz rs, immediate',
            'Branch on Greater Than Zero',
            '000111{rs:05b}00000{imm:016b}',
            InstructionType.B_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'bgtz'


class BgtzalcInstruction(MIPSBasicInstruction):
    """
    Represents the BGTZALC MIPS instruction
    """

    def __init__(self):
        super().__init__(
            'bgtzalc',
            'bgtzalc rt, immediate',
            'Compact branch-and-link if GPR rt is greater than zero',
            '00011100000{rt:05b}{imm:016b}',
            InstructionType.B_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'bgtzalc'


class BgtzcInstruction(MIPSBasicInstruction):
    """
    Represents the BGTZC MIPS instruction
    """

    def __init__(self):
        super().__init__(
            'bgtzc',
            'bgtzc rt, immediate',
            'Branch if Greater Than Zero Compact',
            '01011100000{rt:05b}{imm:016b}',
            InstructionType.B_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'bgtzc'


class BitswapInstruction(MIPSBasicInstruction):
    """
    Represents the BITSWAP MIPS instruction
    """

    def __init__(self):
        super().__init__(
            'bitswap',
            'bitswap rd, rt',
            'Reverse bits in each byte',
            '01111100000{rt:05b}{rd:05b}00000100000',
            InstructionType.R_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'bitswap'


class BlezInstruction(MIPSBasicInstruction):
    """
    Represents the BLEZ MIPS instruction
    """

    def __init__(self):
        super().__init__(
            'blez',
            'blez rs, immediate',
            'Branch on Less Than or Equal to Zero',
            '000110{rs:05b}00000{imm:016b}',
            InstructionType.B_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'blez'


class BlezalcInstruction(MIPSBasicInstruction):
    """
    Represents the BLEZALC MIPS instruction
    """

    def __init__(self):
        super().__init__(
            'blezalc',
            'blezalc rt, immediate',
            'Compact branch-and-link if GPR rt is less than or equal to zero',
            '00011000000{rt:05b}{imm:016b}',
            InstructionType.B_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'blezalc'


class BlezcInstruction(MIPSBasicInstruction):
    """
    Represents the BLEZC MIPS instruction
    """

    def __init__(self):
        super().__init__(
            'blezc',
            'blezc rt, immediate',
            'Branch if Less Than or Equal to Zero Compact',
            '01011000000{rt:05b}{imm:016b}',
            InstructionType.B_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'blezc'


class BltcInstruction(MIPSBasicInstruction):
    """
    Represents the BLTC MIPS instruction
    """

    def __init__(self):
        super().__init__(
            'bltc',
            'bltc rs, rt, immediate',
            'Branch if Less Than Compact (Signed)',
            '010111{rs:05b}{rt:05b}{imm:016b}',
            InstructionType.B_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'bltc'


class BltucInstruction(MIPSBasicInstruction):
    """
    Represents the BLTUC MIPS instruction
    """

    def __init__(self):
        super().__init__(
            'bltuc',
            'bltuc rs, rt, immediate',
            'Branch if Less Than Compact (Unsigned)',
            '000111{rs:05b}{rt:05b}{imm:016b}',
            InstructionType.B_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'bltuc'


class BltzInstruction(MIPSBasicInstruction):
    """
    Represents the BLTZ MIPS instruction
    """

    def __init__(self):
        super().__init__(
            'bltz',
            'bltz rs, immediate',
            'Branch on Less than Zero',
            '000001{rs:05b}00000{imm:016b}',
            InstructionType.B_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'bltz'


class BltzalcInstruction(MIPSBasicInstruction):
    """
    Represents the BLTZALC MIPS instruction
    """

    def __init__(self):
        super().__init__(
            'bltzalc',
            'bltzalc rt, immediate',
            'Compact branch-and-link if GPR rt is less than zero',
            '000111{rt:05b}{rt:05b}{imm:016b}',
            InstructionType.B_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'bltzalc'


class BltzcInstruction(MIPSBasicInstruction):
    """
    Represents the BLTZC MIPS instruction
    """

    def __init__(self):
        super().__init__(
            'bltzc',
            'bltzc rt, immediate',
            'Branch if Less Than Zero Compact',
            '010111{rt:05b}{rt:05b}{imm:016b}',
            InstructionType.B_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'bltzc'


class BneInstruction(MIPSBasicInstruction):
    """
    Represents the BNE MIPS instruction
    """

    def __init__(self):
        super().__init__(
            'bne',
            'bne rs, rt, immediate',
            'Branch on Not Equal',
            '000101{rs:05b}{rt:05b}{imm:016b}',
            InstructionType.B_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'bne'


class BnecInstruction(MIPSBasicInstruction):
    """
    Represents the BNEC MIPS instruction
    """

    def __init__(self):
        super().__init__(
            'bnec',
            'bnec rs, rt, offset',
            'Not-Equal register-register compare and branch with 16-bit offset',
            '011000{rs:05b}{rt:05b}{imm:016b}',
            InstructionType.B_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'bnec'


class BnezalcInstruction(MIPSBasicInstruction):
    """
    Represents the BNEZALC MIPS instruction
    """

    def __init__(self):
        super().__init__(
            'bnezalc',
            'bnezalc rt, immediate',
            'Compact branch-and-link if GPR rt is not equal to zero',
            '01100000000{rt:05b}{imm:016b}',
            InstructionType.B_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'bnezalc'


class BnezcInstruction(MIPSBasicInstruction):
    """
    Represents the BNEZC MIPS instruction
    """

    def __init__(self):
        super().__init__(
            'bnezc',
            'bnezc rs, immediate',
            'Branch if Not Equal to Zero Compact',
            '111110{rs:05b}{imm:021b}',
            InstructionType.B_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'bnezc'


class BnvcInstruction(MIPSBasicInstruction):
    """
    Represents the BNVC MIPS instruction
    """

    def __init__(self):
        super().__init__(
            'bnvc',
            'bnvc rs, rt, immediate',
            'Branch on no Overflow Compact',
            '011000{rs:05b}{rt:05b}{imm:016b}',
            InstructionType.B_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'bnvc'


class BovcInstruction(MIPSBasicInstruction):
    """
    Represents the BOVC MIPS instruction
    """

    def __init__(self):
        super().__init__(
            'bovc',
            'bovc rs, rt, immediate',
            'Branch on Overflow Compact',
            '001000{rs:05b}{rt:05b}{imm:016b}',
            InstructionType.B_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'bovc'


class BreakInstruction(MIPSBasicInstruction):
    """
    Represents the BREAK MIPS instruction
    """

    def __init__(self):
        super().__init__(
            'break',
            'break',
            'Cause a breakpoint exception',
            '00000000000000000000000000001101',
            InstructionType.R_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'break'


class CloInstruction(MIPSBasicInstruction):
    """
    Represents the CLO MIPS instruction
    """

    def __init__(self):
        super().__init__(
            'clo',
            'clo rd, rs',
            'Count Leading Ones in Word',
            '000000{rs:05b}00000{rd:05b}00001010001',
            InstructionType.R_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'clo'


class ClzInstruction(MIPSBasicInstruction):
    """
    Represents the CLZ MIPS instruction
    """

    def __init__(self):
        super().__init__(
            'clz',
            'clz rd, rs',
            'Count Leading Zeroes in Word',
            '000000{rs:05b}00000{rd:05b}00001010000',
            InstructionType.R_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'clz'


class DivInstruction(MIPSBasicInstruction):
    """
    Represents the DIV MIPS instruction
    """

    def __init__(self):
        super().__init__(
            'div',
            'div rd, rs, rt',
            'Divide 32 bit integers and save quotient (Signed)',
            '000000{rs:05b}{rt:05b}{rd:05b}00010011010',
            InstructionType.R_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'div'


class DivuInstruction(MIPSBasicInstruction):
    """
    Represents the DIVU MIPS instruction
    """

    def __init__(self):
        super().__init__(
            'divu',
            'divu rd, rs, rt',
            'Divide 32 bit integers and save quotient',
            '000000{rs:05b}{rt:05b}{rd:05b}00010011011',
            InstructionType.R_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'divu'


class JInstruction(MIPSBasicInstruction):
    """
    Represents the J MIPS instruction
    """

    def __init__(self):
        super().__init__(
            'j',
            'j immediate',
            'Jump to immediate address',
            '000010{imm:026b}',
            InstructionType.J_SHIFT_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'j'


class JalInstruction(MIPSBasicInstruction):
    """
    Represents the JAL MIPS instruction
    """

    def __init__(self):
        super().__init__(
            'jal',
            'jal immediate',
            'Jump and Link to immediate address',
            '000011{imm:026b}',
            InstructionType.J_SHIFT_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'jal'


class JalrInstruction(MIPSBasicInstruction):
    """
    Represents the JALR MIPS instruction
    """

    def __init__(self):
        super().__init__(
            'jalr',
            'jalr rd, rs',
            'Jump and Link to address in GPR[rs]',
            '000000{rs:05b}00000{rd:05b}00000001001',
            InstructionType.J_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'jalr'


class JialcInstruction(MIPSBasicInstruction):
    """
    Represents the JIALC MIPS instruction
    """

    def __init__(self):
        super().__init__(
            'jialc',
            'jialc rt, immediate',
            'Jump Indexed and Link Compact',
            '11111000000{rt:05b}{imm:016b}',
            InstructionType.J_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'jialc'


class JicInstruction(MIPSBasicInstruction):
    """
    Represents the JIC MIPS instruction
    """

    def __init__(self):
        super().__init__(
            'jic',
            'jic rt, immediate',
            'Jump Indexed Compact',
            '11011000000{rt:05b}{imm:016b}',
            InstructionType.J_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'jic'


class LbInstruction(MIPSBasicInstruction):
    """
    Represents the LB MIPS instruction
    """

    def __init__(self):
        super().__init__(
            'lb',
            'lb rt, immediate(rs)',
            'Load Byte from memory as signed value',
            '100000{rs:05b}{rt:05b}{imm:016b}',
            InstructionType.I_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'lb'


class LbuInstruction(MIPSBasicInstruction):
    """
    Represents the LBU MIPS instruction
    """

    def __init__(self):
        super().__init__(
            'lbu',
            'lbu rt, immediate(rs)',
            'Load Byte from memory as unsigned value',
            '100100{rs:05b}{rt:05b}{imm:016b}',
            InstructionType.I_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'lbu'


class LhInstruction(MIPSBasicInstruction):
    """
    Represents the LH MIPS instruction
    """

    def __init__(self):
        super().__init__(
            'lh',
            'lh rt, immediate(rs)',
            'Load Halfword from memory as signed value',
            '100001{rs:05b}{rt:05b}{imm:016b}',
            InstructionType.I_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'lh'


class LhuInstruction(MIPSBasicInstruction):
    """
    Represents the LHU MIPS instruction
    """

    def __init__(self):
        super().__init__(
            'lhu',
            'lhu rt, immediate(rs)',
            'Load Halfword from memory as unsigned value',
            '100101{rs:05b}{rt:05b}{imm:016b}',
            InstructionType.I_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'lhu'


class LwInstruction(MIPSBasicInstruction):
    """
    Represents the LW MIPS instruction
    """

    def __init__(self):
        super().__init__(
            'lw',
            'lw rt, immediate(rs)',
            'Load Word from memory as signed value',
            '100011{rs:05b}{rt:05b}{imm:016b}',
            InstructionType.I_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'lw'


class LwpcInstruction(MIPSBasicInstruction):
    """
    Represents the LWPC MIPS instruction
    """

    def __init__(self):
        super().__init__(
            'lwpc',
            'lwpc rs, immediate',
            'Load Word from memory as signed value using PC-relative address',
            '111011{rs:05b}01{imm:019b}',
            InstructionType.I_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'lwpc'


class Mfc0Instruction(MIPSBasicInstruction):
    """
    Represents the MFC0 MIPS instruction
    """

    def __init__(self):
        super().__init__(
            'mfc0',
            'mfc0 rt, rd, sel',
            'Move from Coprocessor 0',
            '01000000000{rt:05b}{rd:05b}00000000{imm:03b}',
            InstructionType.R_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'mfc0'


class ModInstruction(MIPSBasicInstruction):
    """
    Represents the MOD MIPS instruction
    """

    def __init__(self):
        super().__init__(
            'mod',
            'mod rd, rs, rt',
            'Divide 32 bit integers and save remainder (Signed)',
            '000000{rs:05b}{rt:05b}{rd:05b}00011011010',
            InstructionType.R_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'mod'


class ModuInstruction(MIPSBasicInstruction):
    """
    Represents the MODU MIPS instruction
    """

    def __init__(self):
        super().__init__(
            'modu',
            'modu rd, rs, rt',
            'Divide 32 bit integers and save remainder',
            '000000{rs:05b}{rt:05b}{rd:05b}00011011011',
            InstructionType.R_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'modu'


class Mtc0Instruction(MIPSBasicInstruction):
    """
    Represents the MTC0 MIPS instruction
    """

    def __init__(self):
        super().__init__(
            'mtc0',
            'mtc0 rt, rd, sel',
            'Move to Coprocessor 0',
            '01000000100{rt:05b}{rd:05b}00000000{imm:03b}',
            InstructionType.R_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'mtc0'


class MuhInstruction(MIPSBasicInstruction):
    """
    Represents the MUH MIPS instruction
    """

    def __init__(self):
        super().__init__(
            'muh',
            'muh rd, rs, rt',
            'Multiply 32 bit integers and save high word (Signed)',
            '000000{rs:05b}{rt:05b}{rd:05b}00011011000',
            InstructionType.R_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'muh'


class MuhuInstruction(MIPSBasicInstruction):
    """
    Represents the MUHU MIPS instruction
    """

    def __init__(self):
        super().__init__(
            'muhu',
            'muhu rd, rs, rt',
            'Multiply 32 bit integers and save low word',
            '000000{rs:05b}{rt:05b}{rd:05b}00011011001',
            InstructionType.R_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'muhu'


class MulInstruction(MIPSBasicInstruction):
    """
    Represents the MUL MIPS instruction
    """

    def __init__(self):
        super().__init__(
            'mul',
            'mul rd, rs, rt',
            'Multiply 32 bit integers and save low word (Signed)',
            '000000{rs:05b}{rt:05b}{rd:05b}00010011000',
            InstructionType.R_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'mul'


class MuluInstruction(MIPSBasicInstruction):
    """
    Represents the MULU MIPS instruction
    """

    def __init__(self):
        super().__init__(
            'mulu',
            'mulu rd, rs, rt',
            'Multiply 32 bit integers and save high word',
            '000000{rs:05b}{rt:05b}{rd:05b}00010011001',
            InstructionType.R_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'mulu'


class NorInstruction(MIPSBasicInstruction):
    """
    Represents the NOR MIPS instruction
    """

    def __init__(self):
        super().__init__(
            'nor',
            'nor rd, rs, rt',
            'Bitwise logical NOT OR',
            '000000{rs:05b}{rt:05b}{rd:05b}00000100111',
            InstructionType.R_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'nor'


class OrInstruction(MIPSBasicInstruction):
    """
    Represents the OR MIPS instruction
    """

    def __init__(self):
        super().__init__(
            'or',
            'or rd, rs, rt',
            'Bitwise logical OR',
            '000000{rs:05b}{rt:05b}{rd:05b}00000100101',
            InstructionType.R_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'or'


class OriInstruction(MIPSBasicInstruction):
    """
    Represents the ORI MIPS instruction
    """

    def __init__(self):
        super().__init__(
            'ori',
            'ori rt, rs, immediate',
            'Bitwise OR with immediate',
            '001101{rs:05b}{rt:05b}{imm:016b}',
            InstructionType.I_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'ori'


class SbInstruction(MIPSBasicInstruction):
    """
    Represents the SB MIPS instruction
    """

    def __init__(self):
        super().__init__(
            'sb',
            'sb rt, immediate(rs)',
            'Store Byte in memory',
            '101000{rs:05b}{rt:05b}{imm:016b}',
            InstructionType.I_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'sb'


class SebInstruction(MIPSBasicInstruction):
    """
    Represents the SEB MIPS instruction
    """

    def __init__(self):
        super().__init__(
            'seb',
            'seb, rd, rt',
            'Sign-extend least significant byte',
            '01111100000{rt:05b}{rd:05b}10000100000',
            InstructionType.R_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'seb'


class SehInstruction(MIPSBasicInstruction):
    """
    Represents the SEH MIPS instruction
    """

    def __init__(self):
        super().__init__(
            'seh',
            'seh, rd, rt',
            'Sign-extend least significant halfword',
            '01111100000{rt:05b}{rd:05b}11000100000',
            InstructionType.R_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'seh'


class ShInstruction(MIPSBasicInstruction):
    """
    Represents the SH MIPS instruction
    """

    def __init__(self):
        super().__init__(
            'sh',
            'sh rt, immediate(rs)',
            'Store Halfword in memory',
            '101001{rs:05b}{rt:05b}{imm:016b}',
            InstructionType.I_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'sh'


class SllInstruction(MIPSBasicInstruction):
    """
    Represents the SLL MIPS instruction
    """

    def __init__(self):
        super().__init__(
            'sll',
            'sll rt, rd, immediate',
            'Shift Left Logical with immediate',
            '00000000000{rt:05b}{rd:05b}{imm:05b}000000',
            InstructionType.R_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'sll'


class SllvInstruction(MIPSBasicInstruction):
    """
    Represents the SLLV MIPS instruction
    """

    def __init__(self):
        super().__init__(
            'sllv',
            'sllv rd, rt, rs',
            'Shift Left Logical Variable',
            '000000{rs:05b}{rt:05b}{rd:05b}00000000100',
            InstructionType.R_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'sllv'


class SltInstruction(MIPSBasicInstruction):
    """
    Represents the SLT MIPS instruction
    """

    def __init__(self):
        super().__init__(
            'slt',
            'slt rd, rt, rs',
            'Set on Less Than (Signed)',
            '000000{rs:05b}{rt:05b}{rd:05b}00000101010',
            InstructionType.R_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'slt'


class SltiInstruction(MIPSBasicInstruction):
    """
    Represents the SLTI MIPS instruction
    """

    def __init__(self):
        super().__init__(
            'slti',
            'slti rt, rs, immediate',
            'Set on Less Than Immediate (Signed)',
            '001010{rs:05b}{rt:05b}{imm:016b}',
            InstructionType.I_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'slti'


class SltiuInstruction(MIPSBasicInstruction):
    """
    Represents the SLTIU MIPS instruction
    """

    def __init__(self):
        super().__init__(
            'sltiu',
            'sltiu rt, rs, immediate',
            'Set on Less Than Immediate (Unsigned)',
            '001011{rs:05b}{rt:05b}{imm:016b}',
            InstructionType.I_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'sltiu'


class SltuInstruction(MIPSBasicInstruction):
    """
    Represents the SLTU MIPS instruction
    """

    def __init__(self):
        super().__init__(
            'sltu',
            'sltu rd, rt, rs',
            'Set on Less Than',
            '000000{rs:05b}{rt:05b}{rd:05b}00000101011',
            InstructionType.R_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'sltu'


class SraInstruction(MIPSBasicInstruction):
    """
    Represents the SRA MIPS instruction
    """

    def __init__(self):
        super().__init__(
            'sra',
            'sra rd, rt, immediate',
            'Shift Right Arithmetic (duplicate sign-bit)',
            '00000000000{rt:05b}{rd:05b}{imm:05b}000011',
            InstructionType.R_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'sra'


class SravInstruction(MIPSBasicInstruction):
    """
    Represents the SRAV MIPS instruction
    """

    def __init__(self):
        super().__init__(
            'srav',
            'srav rd, rt, rs',
            'Shift Right Arithmetic Variable (duplicate sign-bit)',
            '000000{rs:05b}{rt:05b}{rd:05b}00000000111',
            InstructionType.R_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'srav'


class SrlInstruction(MIPSBasicInstruction):
    """
    Represents the SRL MIPS instruction
    """

    def __init__(self):
        super().__init__(
            'srl',
            'srl rd, rt, immediate',
            'Shift Right Logical (insert zeroes)',
            '00000000000{rt:05b}{rd:05b}{imm:05b}000010',
            InstructionType.R_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'srl'


class SrlvInstruction(MIPSBasicInstruction):
    """
    Represents the SRLV MIPS instruction
    """

    def __init__(self):
        super().__init__(
            'srlv',
            'srlv rd, rt, rs',
            'Shift Right Logical Variable (insert zeroes)',
            '000000{rs:05b}{rt:05b}{rd:05b}00000000110',
            InstructionType.R_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'srlv'


class SubInstruction(MIPSBasicInstruction):
    """
    Represents the SUB MIPS instruction
    """

    def __init__(self):
        super().__init__(
            'sub',
            'sub rd, rs, rt',
            'Subtraction (trap on overflow)',
            '000000{rs:05b}{rt:05b}{rd:05b}00000100010',
            InstructionType.R_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'sub'


class SubuInstruction(MIPSBasicInstruction):
    """
    Represents the SUBU MIPS instruction
    """

    def __init__(self):
        super().__init__(
            'subu',
            'subu rd, rs, rt',
            'Subtraction',
            '000000{rs:05b}{rt:05b}{rd:05b}00000100011',
            InstructionType.R_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'subu'


class SwInstruction(MIPSBasicInstruction):
    """
    Represents the SW MIPS instruction
    """

    def __init__(self):
        super().__init__(
            'sw',
            'sw rt, immediate(rs)',
            'Store Word in memory',
            '101011{rs:05b}{rt:05b}{imm:016b}',
            InstructionType.I_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'sw'


class SyscallInstruction(MIPSBasicInstruction):
    """
    Represents the SYSCALL MIPS instruction
    """

    def __init__(self):
        super().__init__(
            'syscall',
            'syscall',
            'Cause a System Call exception',
            '00000000000000000000000000001100',
            InstructionType.R_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'syscall'


class TeqInstruction(MIPSBasicInstruction):
    """
    Represents the TEQ MIPS instruction
    """

    def __init__(self):
        super().__init__(
            'teq',
            'teq rs, rt',
            'Trap if Equal',
            '000000{rs:05b}{rt:05b}0000000000110100',
            InstructionType.R_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'teq'


class TgeInstruction(MIPSBasicInstruction):
    """
    Represents the TGE MIPS instruction
    """

    def __init__(self):
        super().__init__(
            'tge',
            'tge rs, rt',
            'Trap if Greater or Equal (Signed)',
            '000000{rs:05b}{rt:05b}0000000000110000',
            InstructionType.R_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'tge'


class TgeuInstruction(MIPSBasicInstruction):
    """
    Represents the TGEU MIPS instruction
    """

    def __init__(self):
        super().__init__(
            'tgeu',
            'tgeu rs, rt',
            'Trap if Greater or Equal',
            '000000{rs:05b}{rt:05b}0000000000110001',
            InstructionType.R_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'tgeu'


class TltInstruction(MIPSBasicInstruction):
    """
    Represents the TLT MIPS instruction
    """

    def __init__(self):
        super().__init__(
            'tlt',
            'tlt rs, rt',
            'Trap if Less Than (Signed)',
            '000000{rs:05b}{rt:05b}0000000000110010',
            InstructionType.R_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'tlt'


class TltuInstruction(MIPSBasicInstruction):
    """
    Represents the TLTU MIPS instruction
    """

    def __init__(self):
        super().__init__(
            'tltu',
            'tltu rs, rt',
            'Trap if Less Than',
            '000000{rs:05b}{rt:05b}0000000000110011',
            InstructionType.R_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'tltu'


class TneInstruction(MIPSBasicInstruction):
    """
    Represents the TNE MIPS instruction
    """

    def __init__(self):
        super().__init__(
            'tne',
            'tne rs, rt',
            'Trap if Not Equal',
            '000000{rs:05b}{rt:05b}0000000000110110',
            InstructionType.R_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'tne'


class XorInstruction(MIPSBasicInstruction):
    """
    Represents the XOR MIPS instruction
    """

    def __init__(self):
        super().__init__(
            'xor',
            'xor rd, rs, rt',
            'Bitwise XOR',
            '000000{rs:05b}{rt:05b}{rd:05b}00000100110',
            InstructionType.R_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'xor'


class XoriInstruction(MIPSBasicInstruction):
    """
    Represents the XORI MIPS instruction
    """

    def __init__(self):
        super().__init__(
            'xori',
            'xori rt, rs, immediate',
            'Bitwise Exclusive OR with Immediate',
            '001110{rs:05b}{rt:05b}{imm:016b}',
            InstructionType.I_TYPE
        )

    @staticmethod
    def mnemonic():
        return 'xori'
