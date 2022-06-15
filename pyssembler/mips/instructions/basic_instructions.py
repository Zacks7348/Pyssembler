"""
rs, rt - operand registers
rd - dest register
imm_x - immediate of size x bits
"""


from typing import List

from pyssembler.mips.tokenizer import tokenize_instr_format, TokenType, Token


class MIPSBaseInstruction:
    """
    The base instruction class all MIPS instructions derive from
    """
    
    MNEMONIC = None
    
    def __init__(self, format_: str):
        self.format = format_
        self.fmt_tokens = tokenize_instr_format(self.format)

    def match(self, tokens: List[Token]) -> bool:
        """
        Returns True if the sequence of tokens matches the formatting
        of this instruction.

        Assumes all whitespaces, comments, and label+colons have been removed
        :param tokens: The sequence tokens to test
        :return: bool
        """
        # Easy check
        if len(tokens) < len(self.fmt_tokens):
            return False

        # First token should be this mnemonic
        if tokens[0].type != TokenType.MNEMONIC or tokens[0].raw_text != self.MNEMONIC:
            return False

        # All tokens should match
        for token, fmt_token in zip(tokens[1:], self.fmt_tokens):
            if token.type != fmt_token.type:
                return False
        return True


class MIPSAddInstruction(MIPSBaseInstruction):
    """
    Represents the ADD MIPS instruction
    """
    
    MNEMONIC = 'add'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSAddiuInstruction(MIPSBaseInstruction):
    """
    Represents the ADDIU MIPS instruction
    """
    
    MNEMONIC = 'addiu'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSAddiupcInstruction(MIPSBaseInstruction):
    """
    Represents the ADDIUPC MIPS instruction
    """
    
    MNEMONIC = 'addiupc'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSAdduInstruction(MIPSBaseInstruction):
    """
    Represents the ADDU MIPS instruction
    """
    
    MNEMONIC = 'addu'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSAlignInstruction(MIPSBaseInstruction):
    """
    Represents the ALIGN MIPS instruction
    """
    
    MNEMONIC = 'align'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSAluipcInstruction(MIPSBaseInstruction):
    """
    Represents the ALUIPC MIPS instruction
    """
    
    MNEMONIC = 'aluipc'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSAndInstruction(MIPSBaseInstruction):
    """
    Represents the AND MIPS instruction
    """
    
    MNEMONIC = 'and'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSAndiInstruction(MIPSBaseInstruction):
    """
    Represents the ANDI MIPS instruction
    """
    
    MNEMONIC = 'andi'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSAuiInstruction(MIPSBaseInstruction):
    """
    Represents the AUI MIPS instruction
    """
    
    MNEMONIC = 'aui'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSAuipcInstruction(MIPSBaseInstruction):
    """
    Represents the AUIPC MIPS instruction
    """
    
    MNEMONIC = 'auipc'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSBalInstruction(MIPSBaseInstruction):
    """
    Represents the BAL MIPS instruction
    """
    
    MNEMONIC = 'bal'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSBalcInstruction(MIPSBaseInstruction):
    """
    Represents the BALC MIPS instruction
    """
    
    MNEMONIC = 'balc'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSBcInstruction(MIPSBaseInstruction):
    """
    Represents the BC MIPS instruction
    """
    
    MNEMONIC = 'bc'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSBeqInstruction(MIPSBaseInstruction):
    """
    Represents the BEQ MIPS instruction
    """
    
    MNEMONIC = 'beq'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSBeqcInstruction(MIPSBaseInstruction):
    """
    Represents the BEQC MIPS instruction
    """
    
    MNEMONIC = 'beqc'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSBeqzalcInstruction(MIPSBaseInstruction):
    """
    Represents the BEQZALC MIPS instruction
    """
    
    MNEMONIC = 'beqzalc'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSBeqzcInstruction(MIPSBaseInstruction):
    """
    Represents the BEQZC MIPS instruction
    """
    
    MNEMONIC = 'beqzc'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSBgecInstruction(MIPSBaseInstruction):
    """
    Represents the BGEC MIPS instruction
    """
    
    MNEMONIC = 'bgec'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSBgeucInstruction(MIPSBaseInstruction):
    """
    Represents the BGEUC MIPS instruction
    """
    
    MNEMONIC = 'bgeuc'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSBgezInstruction(MIPSBaseInstruction):
    """
    Represents the BGEZ MIPS instruction
    """
    
    MNEMONIC = 'bgez'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSBgezalcInstruction(MIPSBaseInstruction):
    """
    Represents the BGEZALC MIPS instruction
    """
    
    MNEMONIC = 'bgezalc'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSBgezcInstruction(MIPSBaseInstruction):
    """
    Represents the BGEZC MIPS instruction
    """
    
    MNEMONIC = 'bgezc'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSBgtzInstruction(MIPSBaseInstruction):
    """
    Represents the BGTZ MIPS instruction
    """
    
    MNEMONIC = 'bgtz'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSBgtzalcInstruction(MIPSBaseInstruction):
    """
    Represents the BGTZALC MIPS instruction
    """
    
    MNEMONIC = 'bgtzalc'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSBgtzcInstruction(MIPSBaseInstruction):
    """
    Represents the BGTZC MIPS instruction
    """
    
    MNEMONIC = 'bgtzc'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSBitswapInstruction(MIPSBaseInstruction):
    """
    Represents the BITSWAP MIPS instruction
    """
    
    MNEMONIC = 'bitswap'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSBlezInstruction(MIPSBaseInstruction):
    """
    Represents the BLEZ MIPS instruction
    """
    
    MNEMONIC = 'blez'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSBlezalcInstruction(MIPSBaseInstruction):
    """
    Represents the BLEZALC MIPS instruction
    """
    
    MNEMONIC = 'blezalc'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSBlezcInstruction(MIPSBaseInstruction):
    """
    Represents the BLEZC MIPS instruction
    """
    
    MNEMONIC = 'blezc'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSBltcInstruction(MIPSBaseInstruction):
    """
    Represents the BLTC MIPS instruction
    """
    
    MNEMONIC = 'bltc'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSBltucInstruction(MIPSBaseInstruction):
    """
    Represents the BLTUC MIPS instruction
    """
    
    MNEMONIC = 'bltuc'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSBltzInstruction(MIPSBaseInstruction):
    """
    Represents the BLTZ MIPS instruction
    """
    
    MNEMONIC = 'bltz'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSBltzalcInstruction(MIPSBaseInstruction):
    """
    Represents the BLTZALC MIPS instruction
    """
    
    MNEMONIC = 'bltzalc'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSBltzcInstruction(MIPSBaseInstruction):
    """
    Represents the BLTZC MIPS instruction
    """
    
    MNEMONIC = 'bltzc'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSBneInstruction(MIPSBaseInstruction):
    """
    Represents the BNE MIPS instruction
    """
    
    MNEMONIC = 'bne'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSBnecInstruction(MIPSBaseInstruction):
    """
    Represents the BNEC MIPS instruction
    """
    
    MNEMONIC = 'bnec'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSBnezalcInstruction(MIPSBaseInstruction):
    """
    Represents the BNEZALC MIPS instruction
    """
    
    MNEMONIC = 'bnezalc'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSBnezcInstruction(MIPSBaseInstruction):
    """
    Represents the BNEZC MIPS instruction
    """
    
    MNEMONIC = 'bnezc'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSBnvcInstruction(MIPSBaseInstruction):
    """
    Represents the BNVC MIPS instruction
    """
    
    MNEMONIC = 'bnvc'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSBovcInstruction(MIPSBaseInstruction):
    """
    Represents the BOVC MIPS instruction
    """
    
    MNEMONIC = 'bovc'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSBreakInstruction(MIPSBaseInstruction):
    """
    Represents the BREAK MIPS instruction
    """
    
    MNEMONIC = 'break'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSCloInstruction(MIPSBaseInstruction):
    """
    Represents the CLO MIPS instruction
    """
    
    MNEMONIC = 'clo'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSClzInstruction(MIPSBaseInstruction):
    """
    Represents the CLZ MIPS instruction
    """
    
    MNEMONIC = 'clz'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSDivInstruction(MIPSBaseInstruction):
    """
    Represents the DIV MIPS instruction
    """
    
    MNEMONIC = 'div'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSDivuInstruction(MIPSBaseInstruction):
    """
    Represents the DIVU MIPS instruction
    """
    
    MNEMONIC = 'divu'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSJInstruction(MIPSBaseInstruction):
    """
    Represents the J MIPS instruction
    """
    
    MNEMONIC = 'j'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSJalInstruction(MIPSBaseInstruction):
    """
    Represents the JAL MIPS instruction
    """
    
    MNEMONIC = 'jal'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSJalrInstruction(MIPSBaseInstruction):
    """
    Represents the JALR MIPS instruction
    """
    
    MNEMONIC = 'jalr'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSJialcInstruction(MIPSBaseInstruction):
    """
    Represents the JIALC MIPS instruction
    """
    
    MNEMONIC = 'jialc'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSJicInstruction(MIPSBaseInstruction):
    """
    Represents the JIC MIPS instruction
    """
    
    MNEMONIC = 'jic'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSLbInstruction(MIPSBaseInstruction):
    """
    Represents the LB MIPS instruction
    """
    
    MNEMONIC = 'lb'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSLbuInstruction(MIPSBaseInstruction):
    """
    Represents the LBU MIPS instruction
    """
    
    MNEMONIC = 'lbu'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSLhInstruction(MIPSBaseInstruction):
    """
    Represents the LH MIPS instruction
    """
    
    MNEMONIC = 'lh'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSLhuInstruction(MIPSBaseInstruction):
    """
    Represents the LHU MIPS instruction
    """
    
    MNEMONIC = 'lhu'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSLwInstruction(MIPSBaseInstruction):
    """
    Represents the LW MIPS instruction
    """
    
    MNEMONIC = 'lw'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSLwpcInstruction(MIPSBaseInstruction):
    """
    Represents the LWPC MIPS instruction
    """
    
    MNEMONIC = 'lwpc'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSMfc0Instruction(MIPSBaseInstruction):
    """
    Represents the MFC0 MIPS instruction
    """
    
    MNEMONIC = 'mfc0'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSModInstruction(MIPSBaseInstruction):
    """
    Represents the MOD MIPS instruction
    """
    
    MNEMONIC = 'mod'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSModuInstruction(MIPSBaseInstruction):
    """
    Represents the MODU MIPS instruction
    """
    
    MNEMONIC = 'modu'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSMtc0Instruction(MIPSBaseInstruction):
    """
    Represents the MTC0 MIPS instruction
    """
    
    MNEMONIC = 'mtc0'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSMuhInstruction(MIPSBaseInstruction):
    """
    Represents the MUH MIPS instruction
    """
    
    MNEMONIC = 'muh'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSMuhuInstruction(MIPSBaseInstruction):
    """
    Represents the MUHU MIPS instruction
    """
    
    MNEMONIC = 'muhu'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSMulInstruction(MIPSBaseInstruction):
    """
    Represents the MUL MIPS instruction
    """
    
    MNEMONIC = 'mul'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSMuluInstruction(MIPSBaseInstruction):
    """
    Represents the MULU MIPS instruction
    """
    
    MNEMONIC = 'mulu'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSNorInstruction(MIPSBaseInstruction):
    """
    Represents the NOR MIPS instruction
    """
    
    MNEMONIC = 'nor'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSOrInstruction(MIPSBaseInstruction):
    """
    Represents the OR MIPS instruction
    """
    
    MNEMONIC = 'or'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSOriInstruction(MIPSBaseInstruction):
    """
    Represents the ORI MIPS instruction
    """
    
    MNEMONIC = 'ori'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSSbInstruction(MIPSBaseInstruction):
    """
    Represents the SB MIPS instruction
    """
    
    MNEMONIC = 'sb'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSSebInstruction(MIPSBaseInstruction):
    """
    Represents the SEB MIPS instruction
    """
    
    MNEMONIC = 'seb'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSSehInstruction(MIPSBaseInstruction):
    """
    Represents the SEH MIPS instruction
    """
    
    MNEMONIC = 'seh'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSShInstruction(MIPSBaseInstruction):
    """
    Represents the SH MIPS instruction
    """
    
    MNEMONIC = 'sh'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSSllInstruction(MIPSBaseInstruction):
    """
    Represents the SLL MIPS instruction
    """
    
    MNEMONIC = 'sll'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSSllvInstruction(MIPSBaseInstruction):
    """
    Represents the SLLV MIPS instruction
    """
    
    MNEMONIC = 'sllv'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSSltInstruction(MIPSBaseInstruction):
    """
    Represents the SLT MIPS instruction
    """
    
    MNEMONIC = 'slt'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSSltiInstruction(MIPSBaseInstruction):
    """
    Represents the SLTI MIPS instruction
    """
    
    MNEMONIC = 'slti'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSSltiuInstruction(MIPSBaseInstruction):
    """
    Represents the SLTIU MIPS instruction
    """
    
    MNEMONIC = 'sltiu'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSSltuInstruction(MIPSBaseInstruction):
    """
    Represents the SLTU MIPS instruction
    """
    
    MNEMONIC = 'sltu'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSSraInstruction(MIPSBaseInstruction):
    """
    Represents the SRA MIPS instruction
    """
    
    MNEMONIC = 'sra'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSSravInstruction(MIPSBaseInstruction):
    """
    Represents the SRAV MIPS instruction
    """
    
    MNEMONIC = 'srav'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSSrlInstruction(MIPSBaseInstruction):
    """
    Represents the SRL MIPS instruction
    """
    
    MNEMONIC = 'srl'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSSrlvInstruction(MIPSBaseInstruction):
    """
    Represents the SRLV MIPS instruction
    """
    
    MNEMONIC = 'srlv'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSSubInstruction(MIPSBaseInstruction):
    """
    Represents the SUB MIPS instruction
    """
    
    MNEMONIC = 'sub'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSSubuInstruction(MIPSBaseInstruction):
    """
    Represents the SUBU MIPS instruction
    """
    
    MNEMONIC = 'subu'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSSwInstruction(MIPSBaseInstruction):
    """
    Represents the SW MIPS instruction
    """
    
    MNEMONIC = 'sw'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSSyscallInstruction(MIPSBaseInstruction):
    """
    Represents the SYSCALL MIPS instruction
    """
    
    MNEMONIC = 'syscall'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSTeqInstruction(MIPSBaseInstruction):
    """
    Represents the TEQ MIPS instruction
    """
    
    MNEMONIC = 'teq'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSTgeInstruction(MIPSBaseInstruction):
    """
    Represents the TGE MIPS instruction
    """
    
    MNEMONIC = 'tge'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSTgeuInstruction(MIPSBaseInstruction):
    """
    Represents the TGEU MIPS instruction
    """
    
    MNEMONIC = 'tgeu'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSTltInstruction(MIPSBaseInstruction):
    """
    Represents the TLT MIPS instruction
    """
    
    MNEMONIC = 'tlt'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSTltuInstruction(MIPSBaseInstruction):
    """
    Represents the TLTU MIPS instruction
    """
    
    MNEMONIC = 'tltu'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSTneInstruction(MIPSBaseInstruction):
    """
    Represents the TNE MIPS instruction
    """
    
    MNEMONIC = 'tne'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSXorInstruction(MIPSBaseInstruction):
    """
    Represents the XOR MIPS instruction
    """
    
    MNEMONIC = 'xor'
    
    def __init__(self):
        super().__init__('format')
    

class MIPSXoriInstruction(MIPSBaseInstruction):
    """
    Represents the XORI MIPS instruction
    """
    
    MNEMONIC = 'xori'
    
    def __init__(self):
        super().__init__('format')
    
