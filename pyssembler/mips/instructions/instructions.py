class BaseInstruction:
    """
    The base instruction class all Pyssembler instructions derive from
    """
    
    MNEMONIC = None
    
    def __init__(self):
        pass
    

class AddInstruction(BaseInstruction):
    """
    Represents the ADD MIPS instruction
    """
    
    MNEMONIC = 'add'
    
    def __init__(self):
        super().__init__()
    

class AddiuInstruction(BaseInstruction):
    """
    Represents the ADDIU MIPS instruction
    """
    
    MNEMONIC = 'addiu'
    
    def __init__(self):
        super().__init__()
    

class AddiupcInstruction(BaseInstruction):
    """
    Represents the ADDIUPC MIPS instruction
    """
    
    MNEMONIC = 'addiupc'
    
    def __init__(self):
        super().__init__()
    

class AdduInstruction(BaseInstruction):
    """
    Represents the ADDU MIPS instruction
    """
    
    MNEMONIC = 'addu'
    
    def __init__(self):
        super().__init__()
    

class AlignInstruction(BaseInstruction):
    """
    Represents the ALIGN MIPS instruction
    """
    
    MNEMONIC = 'align'
    
    def __init__(self):
        super().__init__()
    

class AluipcInstruction(BaseInstruction):
    """
    Represents the ALUIPC MIPS instruction
    """
    
    MNEMONIC = 'aluipc'
    
    def __init__(self):
        super().__init__()
    

class AndInstruction(BaseInstruction):
    """
    Represents the AND MIPS instruction
    """
    
    MNEMONIC = 'and'
    
    def __init__(self):
        super().__init__()
    

class AndiInstruction(BaseInstruction):
    """
    Represents the ANDI MIPS instruction
    """
    
    MNEMONIC = 'andi'
    
    def __init__(self):
        super().__init__()
    

class AuiInstruction(BaseInstruction):
    """
    Represents the AUI MIPS instruction
    """
    
    MNEMONIC = 'aui'
    
    def __init__(self):
        super().__init__()
    

class AuipcInstruction(BaseInstruction):
    """
    Represents the AUIPC MIPS instruction
    """
    
    MNEMONIC = 'auipc'
    
    def __init__(self):
        super().__init__()
    

class BalInstruction(BaseInstruction):
    """
    Represents the BAL MIPS instruction
    """
    
    MNEMONIC = 'bal'
    
    def __init__(self):
        super().__init__()
    

class BalcInstruction(BaseInstruction):
    """
    Represents the BALC MIPS instruction
    """
    
    MNEMONIC = 'balc'
    
    def __init__(self):
        super().__init__()
    

class BcInstruction(BaseInstruction):
    """
    Represents the BC MIPS instruction
    """
    
    MNEMONIC = 'bc'
    
    def __init__(self):
        super().__init__()
    

class BeqInstruction(BaseInstruction):
    """
    Represents the BEQ MIPS instruction
    """
    
    MNEMONIC = 'beq'
    
    def __init__(self):
        super().__init__()
    

class BeqcInstruction(BaseInstruction):
    """
    Represents the BEQC MIPS instruction
    """
    
    MNEMONIC = 'beqc'
    
    def __init__(self):
        super().__init__()
    

class BeqzalcInstruction(BaseInstruction):
    """
    Represents the BEQZALC MIPS instruction
    """
    
    MNEMONIC = 'beqzalc'
    
    def __init__(self):
        super().__init__()
    

class BeqzcInstruction(BaseInstruction):
    """
    Represents the BEQZC MIPS instruction
    """
    
    MNEMONIC = 'beqzc'
    
    def __init__(self):
        super().__init__()
    

class BgecInstruction(BaseInstruction):
    """
    Represents the BGEC MIPS instruction
    """
    
    MNEMONIC = 'bgec'
    
    def __init__(self):
        super().__init__()
    

class BgeucInstruction(BaseInstruction):
    """
    Represents the BGEUC MIPS instruction
    """
    
    MNEMONIC = 'bgeuc'
    
    def __init__(self):
        super().__init__()
    

class BgezInstruction(BaseInstruction):
    """
    Represents the BGEZ MIPS instruction
    """
    
    MNEMONIC = 'bgez'
    
    def __init__(self):
        super().__init__()
    

class BgezalcInstruction(BaseInstruction):
    """
    Represents the BGEZALC MIPS instruction
    """
    
    MNEMONIC = 'bgezalc'
    
    def __init__(self):
        super().__init__()
    

class BgezcInstruction(BaseInstruction):
    """
    Represents the BGEZC MIPS instruction
    """
    
    MNEMONIC = 'bgezc'
    
    def __init__(self):
        super().__init__()
    

class BgtzInstruction(BaseInstruction):
    """
    Represents the BGTZ MIPS instruction
    """
    
    MNEMONIC = 'bgtz'
    
    def __init__(self):
        super().__init__()
    

class BgtzalcInstruction(BaseInstruction):
    """
    Represents the BGTZALC MIPS instruction
    """
    
    MNEMONIC = 'bgtzalc'
    
    def __init__(self):
        super().__init__()
    

class BgtzcInstruction(BaseInstruction):
    """
    Represents the BGTZC MIPS instruction
    """
    
    MNEMONIC = 'bgtzc'
    
    def __init__(self):
        super().__init__()
    

class BitswapInstruction(BaseInstruction):
    """
    Represents the BITSWAP MIPS instruction
    """
    
    MNEMONIC = 'bitswap'
    
    def __init__(self):
        super().__init__()
    

class BlezInstruction(BaseInstruction):
    """
    Represents the BLEZ MIPS instruction
    """
    
    MNEMONIC = 'blez'
    
    def __init__(self):
        super().__init__()
    

class BlezalcInstruction(BaseInstruction):
    """
    Represents the BLEZALC MIPS instruction
    """
    
    MNEMONIC = 'blezalc'
    
    def __init__(self):
        super().__init__()
    

class BlezcInstruction(BaseInstruction):
    """
    Represents the BLEZC MIPS instruction
    """
    
    MNEMONIC = 'blezc'
    
    def __init__(self):
        super().__init__()
    

class BltcInstruction(BaseInstruction):
    """
    Represents the BLTC MIPS instruction
    """
    
    MNEMONIC = 'bltc'
    
    def __init__(self):
        super().__init__()
    

class BltucInstruction(BaseInstruction):
    """
    Represents the BLTUC MIPS instruction
    """
    
    MNEMONIC = 'bltuc'
    
    def __init__(self):
        super().__init__()
    

class BltzInstruction(BaseInstruction):
    """
    Represents the BLTZ MIPS instruction
    """
    
    MNEMONIC = 'bltz'
    
    def __init__(self):
        super().__init__()
    

class BltzalcInstruction(BaseInstruction):
    """
    Represents the BLTZALC MIPS instruction
    """
    
    MNEMONIC = 'bltzalc'
    
    def __init__(self):
        super().__init__()
    

class BltzcInstruction(BaseInstruction):
    """
    Represents the BLTZC MIPS instruction
    """
    
    MNEMONIC = 'bltzc'
    
    def __init__(self):
        super().__init__()
    

class BneInstruction(BaseInstruction):
    """
    Represents the BNE MIPS instruction
    """
    
    MNEMONIC = 'bne'
    
    def __init__(self):
        super().__init__()
    

class BnecInstruction(BaseInstruction):
    """
    Represents the BNEC MIPS instruction
    """
    
    MNEMONIC = 'bnec'
    
    def __init__(self):
        super().__init__()
    

class BnezalcInstruction(BaseInstruction):
    """
    Represents the BNEZALC MIPS instruction
    """
    
    MNEMONIC = 'bnezalc'
    
    def __init__(self):
        super().__init__()
    

class BnezcInstruction(BaseInstruction):
    """
    Represents the BNEZC MIPS instruction
    """
    
    MNEMONIC = 'bnezc'
    
    def __init__(self):
        super().__init__()
    

class BnvcInstruction(BaseInstruction):
    """
    Represents the BNVC MIPS instruction
    """
    
    MNEMONIC = 'bnvc'
    
    def __init__(self):
        super().__init__()
    

class BovcInstruction(BaseInstruction):
    """
    Represents the BOVC MIPS instruction
    """
    
    MNEMONIC = 'bovc'
    
    def __init__(self):
        super().__init__()
    

class BreakInstruction(BaseInstruction):
    """
    Represents the BREAK MIPS instruction
    """
    
    MNEMONIC = 'break'
    
    def __init__(self):
        super().__init__()
    

class CloInstruction(BaseInstruction):
    """
    Represents the CLO MIPS instruction
    """
    
    MNEMONIC = 'clo'
    
    def __init__(self):
        super().__init__()
    

class ClzInstruction(BaseInstruction):
    """
    Represents the CLZ MIPS instruction
    """
    
    MNEMONIC = 'clz'
    
    def __init__(self):
        super().__init__()
    

class DivInstruction(BaseInstruction):
    """
    Represents the DIV MIPS instruction
    """
    
    MNEMONIC = 'div'
    
    def __init__(self):
        super().__init__()
    

class DivuInstruction(BaseInstruction):
    """
    Represents the DIVU MIPS instruction
    """
    
    MNEMONIC = 'divu'
    
    def __init__(self):
        super().__init__()
    

class JInstruction(BaseInstruction):
    """
    Represents the J MIPS instruction
    """
    
    MNEMONIC = 'j'
    
    def __init__(self):
        super().__init__()
    

class JalInstruction(BaseInstruction):
    """
    Represents the JAL MIPS instruction
    """
    
    MNEMONIC = 'jal'
    
    def __init__(self):
        super().__init__()
    

class JalrInstruction(BaseInstruction):
    """
    Represents the JALR MIPS instruction
    """
    
    MNEMONIC = 'jalr'
    
    def __init__(self):
        super().__init__()
    

class JialcInstruction(BaseInstruction):
    """
    Represents the JIALC MIPS instruction
    """
    
    MNEMONIC = 'jialc'
    
    def __init__(self):
        super().__init__()
    

class JicInstruction(BaseInstruction):
    """
    Represents the JIC MIPS instruction
    """
    
    MNEMONIC = 'jic'
    
    def __init__(self):
        super().__init__()
    

class LbInstruction(BaseInstruction):
    """
    Represents the LB MIPS instruction
    """
    
    MNEMONIC = 'lb'
    
    def __init__(self):
        super().__init__()
    

class LbuInstruction(BaseInstruction):
    """
    Represents the LBU MIPS instruction
    """
    
    MNEMONIC = 'lbu'
    
    def __init__(self):
        super().__init__()
    

class LhInstruction(BaseInstruction):
    """
    Represents the LH MIPS instruction
    """
    
    MNEMONIC = 'lh'
    
    def __init__(self):
        super().__init__()
    

class LhuInstruction(BaseInstruction):
    """
    Represents the LHU MIPS instruction
    """
    
    MNEMONIC = 'lhu'
    
    def __init__(self):
        super().__init__()
    

class LwInstruction(BaseInstruction):
    """
    Represents the LW MIPS instruction
    """
    
    MNEMONIC = 'lw'
    
    def __init__(self):
        super().__init__()
    

class LwpcInstruction(BaseInstruction):
    """
    Represents the LWPC MIPS instruction
    """
    
    MNEMONIC = 'lwpc'
    
    def __init__(self):
        super().__init__()
    

class Mfc0Instruction(BaseInstruction):
    """
    Represents the MFC0 MIPS instruction
    """
    
    MNEMONIC = 'mfc0'
    
    def __init__(self):
        super().__init__()
    

class ModInstruction(BaseInstruction):
    """
    Represents the MOD MIPS instruction
    """
    
    MNEMONIC = 'mod'
    
    def __init__(self):
        super().__init__()
    

class ModuInstruction(BaseInstruction):
    """
    Represents the MODU MIPS instruction
    """
    
    MNEMONIC = 'modu'
    
    def __init__(self):
        super().__init__()
    

class Mtc0Instruction(BaseInstruction):
    """
    Represents the MTC0 MIPS instruction
    """
    
    MNEMONIC = 'mtc0'
    
    def __init__(self):
        super().__init__()
    

class MuhInstruction(BaseInstruction):
    """
    Represents the MUH MIPS instruction
    """
    
    MNEMONIC = 'muh'
    
    def __init__(self):
        super().__init__()
    

class MuhuInstruction(BaseInstruction):
    """
    Represents the MUHU MIPS instruction
    """
    
    MNEMONIC = 'muhu'
    
    def __init__(self):
        super().__init__()
    

class MulInstruction(BaseInstruction):
    """
    Represents the MUL MIPS instruction
    """
    
    MNEMONIC = 'mul'
    
    def __init__(self):
        super().__init__()
    

class MuluInstruction(BaseInstruction):
    """
    Represents the MULU MIPS instruction
    """
    
    MNEMONIC = 'mulu'
    
    def __init__(self):
        super().__init__()
    

class NorInstruction(BaseInstruction):
    """
    Represents the NOR MIPS instruction
    """
    
    MNEMONIC = 'nor'
    
    def __init__(self):
        super().__init__()
    

class OrInstruction(BaseInstruction):
    """
    Represents the OR MIPS instruction
    """
    
    MNEMONIC = 'or'
    
    def __init__(self):
        super().__init__()
    

class OriInstruction(BaseInstruction):
    """
    Represents the ORI MIPS instruction
    """
    
    MNEMONIC = 'ori'
    
    def __init__(self):
        super().__init__()
    

class SbInstruction(BaseInstruction):
    """
    Represents the SB MIPS instruction
    """
    
    MNEMONIC = 'sb'
    
    def __init__(self):
        super().__init__()
    

class SebInstruction(BaseInstruction):
    """
    Represents the SEB MIPS instruction
    """
    
    MNEMONIC = 'seb'
    
    def __init__(self):
        super().__init__()
    

class SehInstruction(BaseInstruction):
    """
    Represents the SEH MIPS instruction
    """
    
    MNEMONIC = 'seh'
    
    def __init__(self):
        super().__init__()
    

class ShInstruction(BaseInstruction):
    """
    Represents the SH MIPS instruction
    """
    
    MNEMONIC = 'sh'
    
    def __init__(self):
        super().__init__()
    

class SllInstruction(BaseInstruction):
    """
    Represents the SLL MIPS instruction
    """
    
    MNEMONIC = 'sll'
    
    def __init__(self):
        super().__init__()
    

class SllvInstruction(BaseInstruction):
    """
    Represents the SLLV MIPS instruction
    """
    
    MNEMONIC = 'sllv'
    
    def __init__(self):
        super().__init__()
    

class SltInstruction(BaseInstruction):
    """
    Represents the SLT MIPS instruction
    """
    
    MNEMONIC = 'slt'
    
    def __init__(self):
        super().__init__()
    

class SltiInstruction(BaseInstruction):
    """
    Represents the SLTI MIPS instruction
    """
    
    MNEMONIC = 'slti'
    
    def __init__(self):
        super().__init__()
    

class SltiuInstruction(BaseInstruction):
    """
    Represents the SLTIU MIPS instruction
    """
    
    MNEMONIC = 'sltiu'
    
    def __init__(self):
        super().__init__()
    

class SltuInstruction(BaseInstruction):
    """
    Represents the SLTU MIPS instruction
    """
    
    MNEMONIC = 'sltu'
    
    def __init__(self):
        super().__init__()
    

class SraInstruction(BaseInstruction):
    """
    Represents the SRA MIPS instruction
    """
    
    MNEMONIC = 'sra'
    
    def __init__(self):
        super().__init__()
    

class SravInstruction(BaseInstruction):
    """
    Represents the SRAV MIPS instruction
    """
    
    MNEMONIC = 'srav'
    
    def __init__(self):
        super().__init__()
    

class SrlInstruction(BaseInstruction):
    """
    Represents the SRL MIPS instruction
    """
    
    MNEMONIC = 'srl'
    
    def __init__(self):
        super().__init__()
    

class SrlvInstruction(BaseInstruction):
    """
    Represents the SRLV MIPS instruction
    """
    
    MNEMONIC = 'srlv'
    
    def __init__(self):
        super().__init__()
    

class SubInstruction(BaseInstruction):
    """
    Represents the SUB MIPS instruction
    """
    
    MNEMONIC = 'sub'
    
    def __init__(self):
        super().__init__()
    

class SubuInstruction(BaseInstruction):
    """
    Represents the SUBU MIPS instruction
    """
    
    MNEMONIC = 'subu'
    
    def __init__(self):
        super().__init__()
    

class SwInstruction(BaseInstruction):
    """
    Represents the SW MIPS instruction
    """
    
    MNEMONIC = 'sw'
    
    def __init__(self):
        super().__init__()
    

class SyscallInstruction(BaseInstruction):
    """
    Represents the SYSCALL MIPS instruction
    """
    
    MNEMONIC = 'syscall'
    
    def __init__(self):
        super().__init__()
    

class TeqInstruction(BaseInstruction):
    """
    Represents the TEQ MIPS instruction
    """
    
    MNEMONIC = 'teq'
    
    def __init__(self):
        super().__init__()
    

class TgeInstruction(BaseInstruction):
    """
    Represents the TGE MIPS instruction
    """
    
    MNEMONIC = 'tge'
    
    def __init__(self):
        super().__init__()
    

class TgeuInstruction(BaseInstruction):
    """
    Represents the TGEU MIPS instruction
    """
    
    MNEMONIC = 'tgeu'
    
    def __init__(self):
        super().__init__()
    

class TltInstruction(BaseInstruction):
    """
    Represents the TLT MIPS instruction
    """
    
    MNEMONIC = 'tlt'
    
    def __init__(self):
        super().__init__()
    

class TltuInstruction(BaseInstruction):
    """
    Represents the TLTU MIPS instruction
    """
    
    MNEMONIC = 'tltu'
    
    def __init__(self):
        super().__init__()
    

class TneInstruction(BaseInstruction):
    """
    Represents the TNE MIPS instruction
    """
    
    MNEMONIC = 'tne'
    
    def __init__(self):
        super().__init__()
    

class XorInstruction(BaseInstruction):
    """
    Represents the XOR MIPS instruction
    """
    
    MNEMONIC = 'xor'
    
    def __init__(self):
        super().__init__()
    

class XoriInstruction(BaseInstruction):
    """
    Represents the XORI MIPS instruction
    """
    
    MNEMONIC = 'xori'
    
    def __init__(self):
        super().__init__()
    
