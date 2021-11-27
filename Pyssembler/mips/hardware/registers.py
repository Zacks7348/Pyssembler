"""
This file contains the logic for simulating MIPS32 registers. Registers may be accessed
by accessing the read/write functions provided in the GPR and CP0 objects. The classes
in this class are not meant to be initialized by the user, but instead are used to 
create the GPR and CP0 global objects
"""

from typing import Union, Tuple
from ctypes import c_uint32, c_int32

from .memory import MemorySize
from .utils import Integer


class _Processor:
    """
    Base class for MIPS Processor Register Files 
    """

    def __init__(self) -> None:
        self._regs = {}
        self.reg_names = {}
        self._formatting = {int: '{}', hex: '0x{:08x}', bin: '{:032b}'}

    def is_register(self, name: str) -> bool:
        """
        Returns True if name is a valid register name
        """
        return name in self.reg_names

    def get_addr(self, name: str) -> int:
        """
        Returns address of register name or None if name is invalid
        """
        return self.reg_names.get(name, None)

    def get_name_from_address(self, addr: int) -> str:
        """
        Return the name of the register with address addr 
        or None if invalid address
        """
        for name in self.reg_names:
            if self.reg_names[name] == addr:
                return name
        return None

    def read(self, reg: Union[int, str], signed=False) -> int:
        """
        Return the value in a register

        Parameters
        ----------
        reg: int, str
            The address or name of register to read
        """

        if type(reg) == str:
            if not reg in self.reg_names:
                raise ValueError('Invalid Register name {}'.format(reg))
            reg = self.reg_names[reg]
        if not reg in self._regs:
            raise ValueError('Invalid Register address {}'.format(reg))
        if signed:
            # Convert unsigned int to signed
            return c_int32(self._regs[reg]).value
        return self._regs[reg]

    def write(self, reg: Union[int, str], val: int) -> None:
        """
        Write a value into a register. Values are stored as a 32 bit unsigned
        integer. Only the low 32 bits are stored if val is larger than 32 bits

        Parameters
        ----------
        reg: int, str
            The address or name of register to write to
        """

        if type(reg) == str:
            reg = self.get_addr(reg)
            if reg is None:
                raise ValueError('Invalid Register name {}'.format(reg))
        if not reg in self._regs:
            raise ValueError('Invalid Register address {}'.format(reg))
        self._regs[reg] = c_uint32(val).value
    
    def dump(self, radix=int, signed=True) -> dict:
        """
        Dump the current state of the Register File

        Parameters
        ----------
        radix: class, default=int
            How values are displayed {int, hex, bin}
        
        Returns
        -------
        dict
            A Dictionary of all register addresses in the following
            format: {addr: val}
        """

        dumped = {}
        for name, addr in self.reg_names.items():
            if signed:
                dumped[name] = self._formatting[radix].format(c_int32(self._regs[addr]).value)
            else:
                dumped[name] = self._formatting[radix].format(self._regs[addr])
        return dumped

class _GPR(_Processor):
    """
    Represents MIPS General Purpose Registers 
    """
    def __init__(self) -> None:
        super().__init__()
        self.reg_names = {'$zero': 0, '$at': 1, '$v0': 2, '$v1': 3,
                      '$a0': 4, '$a1': 5, '$a2': 6, '$a3': 7,
                      '$t0': 8, '$t1': 9, '$t2': 10, '$t3': 11,
                      '$t4': 12, '$t5': 13, '$t6': 14, '$t7': 15,
                      '$s0': 16, '$s1': 17, '$s2': 18, '$s3': 19,
                      '$s4': 20, '$s5': 21, '$s6': 22, '$s7': 23,
                      '$t8': 24, '$t9': 25, '$k0': 26, '$k1': 27,
                      '$gp': 28, '$sp': 29, '$fp': 30, '$ra': 31}
        self._regs = {addr: 0 for addr in self.reg_names.values()}
        self.pc = 0
    
    def increment_pc(self):
        """
        Increment the Program Counter
        """
        self.pc += MemorySize.WORD_LENGTH_BYTES
    
    def dump(self, radix=int) -> dict:
        """
        Dump the current state of the General Purpose Register File

        Parameters
        ----------
        radix: class, default=int
            How values are displayed {int, hex, bin}
        
        Returns
        -------
        dict
            A Dictionary of all register addresses in the following
            format: {addr: val}
        """
        dumped = super().dump(radix=radix)
        # These registers should be unsigned
        dumped['$gp'] = self._formatting[radix].format(self._regs[28])
        dumped['$sp'] = self._formatting[radix].format(self._regs[29])
        dumped['$fp'] = self._formatting[radix].format(self._regs[30])
        dumped['ra'] = self._formatting[radix].format(self._regs[31])
        # Add PC since it is not in self.reg_names
        dumped['PC'] = self._formatting[radix].format(self.pc)
        return dumped

class _CP0(_Processor):
    """
    Represents MIPS CP0 registers
    """

    def __init__(self) -> None:
        super().__init__()
        self.reg_names = {'$8': 8, '$12': 12, '$13': 13, '$14': 14}
        self._regs = {addr: 0 for addr in self.reg_names.values()}
        self.VADDR = 8
        self.STATUS = 12
        self.CAUSE = 13
        self.EPC = 14
    
    def read_status(self) -> Tuple[int, int, int, int]:
        """
        Shortcut for reading STATUS register bit values

        Returns
        -------
        tuple
            (int mask, user mode, exc lvl, int enable)
        """
        val = self.read(self.STATUS)
        int_mask = Integer.get_bits(val, 8, 15)
        user_mode = Integer.get_bit(val, 4)
        exc_lvl = Integer.get_bit(val, 1)
        int_enable = Integer.get_bit(val, 0)

        return int_mask, user_mode, exc_lvl, int_enable
    
    def write_status(self, int_mask=None, user_mode=None, exc_lvl=None, int_enable=None) -> None:
        """
        Shortcut for modifying specific bit values in the STATUS register
        """
        val = self.read(self.STATUS)
        if not int_mask is None and type(int_mask) == int:
            val = Integer.change_bits(val, 8, 15, int_mask)
        if not user_mode is None and type(user_mode) == int:
            val = Integer.change_bit(val, 4, user_mode)
        if not exc_lvl is None and type(exc_lvl) == int:
            val = Integer.change_bit(val, 1, exc_lvl)
        if not int_enable is None and type(int_enable) == int:
            val = Integer.change_bit(val, 0, int_enable)
        self.write(self.STATUS, val)
    
    def write_cause(self, b_delay=None, p_ints=None, exc_code=None):
        """
        Shortcut for modifying specific bit values in the CAUSE register
        """
        val = self.read(self.CAUSE)
        if not b_delay is None and type(b_delay) == int:
            val = Integer.change_bit(val, 31, b_delay)
        if not p_ints is None and type(p_ints) == int:
            val = Integer.change_bits(val, 8, 15, p_ints)
        if not exc_code is None and type(exc_code) == int:
            val = Integer.change_bits(val, 2, 6, exc_code)
        self.write(self.CAUSE, val)

    
    def read_cause(self) -> Tuple[int, int, int]:
        """
        Shortcut for reading CAUSE register bit values

        Returns
        -------
        tuple
            (b_delay, pending_int, exc_code)
        """
        val = self.read(self.CAUSE)
        b_delay = Integer.get_bit(val, 31)
        pending_int = Integer.get_bits(val, 8, 15)
        exc_code = Integer.get_bits(val, 2, 6)

        return b_delay, pending_int, exc_code
    
    def dump(self, radix=int) -> dict:
        return super().dump(radix=radix, signed=False)
    

GPR = _GPR()
CP0 = _CP0()

def is_register(name: str) -> bool:
    """
    Returns True if name is a valid GPR or CP0 register name

    Parameters
    ----------
    name : str
        name of register to test

    Returns
    -------
    bool
        True if name is a register name, False otherwise
    """

    return GPR.is_register(name) or CP0.is_register(name)

def get_names() -> list:
    """
    Returns a list of all valid register names for app processors
    """

    # Cast to set first to remove duplicates
    return list(set(list(GPR.reg_names.keys()) + list(CP0.reg_names.keys())))