class CP0:
    """
    Coprocessor 0: System Control Coprocessor

    Pyssembler only uses a subset of CP0 features:
    * Exception handling
    * Switching between user and kernel scripts

    Implements the following registers:
    * $8 (BadVAddr) - Captures the address that caused an 
        Address error (AdEL or AdES)
    * $12 (STATUS) - contains operating mode, interrupt handling,
        and diagnostic states of the processor
    * $13 (CAUSE) - describes cause of most recent exception
    * $14 (EPC) - PC address at last exception
    """
    def __init__(self) -> None:
        self.DEFAULT_STATUS = 0x0000FF11
        self.regs = {8: 0, 12: self.DEFAULT_STATUS, 13: 0, 14: 0} 
    
    def write(self, addr: int, value: int):
        if addr not in self.regs:
            raise ValueError('Invalid address for CP0 write')
        self.regs[addr] = value
    
    def read(self, addr: int):
        if addr not in self.regs:
            raise ValueError('Invalid address for CP0 write')
        return self.regs[addr]
    
class CP1:
    """
    Coprocessor 1: FPU

    Uses the following datatypes:
    * single precision (32 bits, S)
        1[8-bit exponent][23-bit fraction]
    * double precision (64 bits, D)
        1[11-bit exponent][52-bit fraction]
    """
    def __init__(self) -> None:
        pass
        self.regs = {}
        for i in range(32):
            self.regs[i] = [0, '$f'+str(i)]
    
    def write_single(self, addr:int, val:float) -> None:
        if not addr in self.regs:
            raise ValueError('Invalid FPU reg address')
        self.regs[addr][0] = val
    
    def write_double(self, addr:int, val:float) -> None:
        if not addr in self.regs:
            raise ValueError('Invalid FPU reg address')
        if addr % 2 != 0:
            raise ValueError('FPU register must be multiple of 2 to write double!')
        self.regs[addr+1] = val
        self.regs[addr] = val