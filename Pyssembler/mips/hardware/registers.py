from os import name
from typing import Union

from .memory import MAX_UINT32, MIN_SINT32

GP_REGS = {'$zero': 0, '$at': 1, '$v0': 2, '$v1': 3,
                 '$a0': 4, '$a1': 5, '$a2': 6, '$a3': 7,
                 '$t0': 8, '$t1': 9, '$t2': 10, '$t3': 11,
                 '$t4': 12, '$t5': 13, '$t6': 14, '$t7': 15,
                 '$s0': 16, '$s1': 17, '$s2': 18, '$s3': 19,
                 '$s4': 20, '$s5': 21, '$s6': 22, '$s7': 23,
                 '$t8': 24, '$t9': 25, '$k0': 26, '$k1': 27,
                 '$gp': 27, '$sp': 28, '$fp': 29, '$ra': 30,
                 'PC': 31}

CP0_REGS = {'$8': 8, '$12': 12, '$13': 13, '$14': 14}


class RegisterFile:
    """
    Represents a MIPS 32bit RegisterFile

    Used as a base class for GPR and coprocessors 
    """

    def __init__(self, registers, register_names) -> None:
        self.registers = registers
        self.register_names = register_names

    def read(self, reg: Union[int, str]) -> int:
        """
        Function for reading a value of a register.

        Can either pass address of register or name of register.
        """
        if type(reg) == str:  # Read register by name
            if not reg in self.register_names:
                raise ValueError('Invalid Register name {}'.format(reg))
            return self.registers[self.register_names.index(reg)]
        elif type(reg) == int:  # Read register by address
            if not reg in self.registers:
                raise ValueError('Invalid Register address {}'.format(reg))
            return self.registers[reg]

    def write(self, reg: Union[int, str], val: int) -> None:
        """
        Function for writing a value to a register

        Can either pass address of register or name of register. If 
        """
        if type(reg) == str:
            if not reg in self.register_names:
                raise ValueError('Invalid Register name {}'.format(reg))
            reg = self.register_names[reg]
        elif type(reg) == int:
            if not reg in self.registers:
                raise ValueError('Invalid Register address {}'.format(reg))
        if not MIN_SINT32 <= val <= MAX_UINT32:
            raise ValueError('Invalid Val {}'.format(val))
        self.registers[reg] = val
    
    def print(self, radix=int):
        formatting = {int: '{}', hex: '0x{:08x}', bin: '{:032b}'}
        for register, addr in self.register_names.items():
            print(('{}: '+formatting[radix]
                   ).format(register, self.registers[addr]))

    def __str__(self) -> str:
        output = '-------REG-------\n'
        for register, addr in self.register_names.items():
            output += '{:<5}: 0x{:08x}\n'.format(register, self.registers[addr])
        output += '-----------------\n'
        return output


class GPR(RegisterFile):
    def __init__(self) -> None:
        registers = {}
        for addr in GP_REGS.values():
            registers[addr] = 0
        super().__init__(registers, GP_REGS)

    def increment_pc(self):
        self.registers[GP_REGS['PC']] += 4

    @property
    def PC(self):
        return self.registers[GP_REGS['PC']]

class Coprocessor0(RegisterFile):
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
        registers = {}
        for addr in CP0_REGS.values():
            registers[addr] = 0
        super().__init__(registers, CP0_REGS)
