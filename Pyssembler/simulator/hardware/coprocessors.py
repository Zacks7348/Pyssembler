import json
import os

from ..utils import Integer, MAX_UINT32

REGISTERS = os.path.dirname(__file__)+'/../registers.json'

class CP0:
    """
    Represents Coprocessor 0 in MIPS32

    Only implements a subset of features

    Exception Codes:
    0  - INT     (Interrupt)
    4  - ADDRL   (Load from an illegal address)
    5  - ADDRS   (Store to an illegal address)
    8  - SYSCALL (syscall instruction executed)
    9  - BKPT    (break instruction executed)
    10 - RI      (Reserved instruction)
    12 - OVF     (Arithmetic overflow)
    13 - TE      (Trap exception)
    15 - DBZ     (Divide by zero)
    """
    def __init__(self) -> None:
        self.regs = {}
        self.regs_name = {}
        with open (REGISTERS, 'r') as f:
            for name, addr in json.load(f)["CP0"].items():
                self.regs[addr] = [0, name]
                self.regs_name[name] = self.regs[addr]
    
        self.write(0x0000ff11, addr=12)
    
    def read(self, addr=None, name=None):
        """
        Function for reading a value of a register.

        Can either pass address of register or name of register. If name is not None,
        register is accessed by name and anything passed in addr is ignored
        """
        if not addr and not name:
            raise ValueError('Must pass either register address or name')
        if name:
            if name not in self.regs_name:
                raise ValueError('Invalid Register Name')
            return self.regs_name[name][0]
        if not addr in self.regs:
            raise ValueError('Invalid Register Address')
        return self.regs[addr][0]
    
    def write(self, val: int, addr=None, name=None):
        """
        Function for writing a value to a CP0 Register

        Can either pass address of register or name of register. If name is not None,
        register is accessed by name and anything passed in addr is ignored
        """
        if not 0 <= val <= MAX_UINT32:
            raise ValueError('Invalid value')
        if not addr and not name:
            raise ValueError('Must pass either register address or name')
        if name:
            if name not in self.regs_name:
                raise ValueError('Invalid Register Name')
            self.regs_name[name][0] = val
            return
        if not addr in self.regs:
            raise ValueError('Invalid CP0 Register Address')
        self.regs[addr][0] = val

    def get_regs(self):
        return {values[1]:addr for (addr, values) in self.regs.items()}

    # Util functions for reading specific bits from the registers
    @property
    def interrupt_enable(self):
        # bit 0 of Status Register
        return self.regs[12] & 0x00000001
    @property
    def exception_level(self):
        # bit 1 of Status Register
        return (self.regs[12] & 0x00000002) >> 1
    @property
    def user_mode(self):
        # bit 4 of Status Register
        return (self.regs[12] & 0x00000010) >> 4
    @property
    def interrupt_mask(self):
        # bits 15-8 of Status Register
        return (self.regs[12] & 0x0000ff00) >> 8
    @property
    def exception_code(self):
        # bits 6-2 of Cause Register
        return (self.regs[13] & 0x0000007c) >> 2
    @property
    def pending_interrupts(self):
        # bits 15-8 of Cause Register
        return (self.regs[13] & 0x0000ff00) >> 8
    @property
    def branch_delay(self):
        # bit 31 of Cause Register
        return (self.regs[13] & 0x80000000) >> 31