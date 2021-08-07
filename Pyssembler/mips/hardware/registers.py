"""MIPS32 REGISTERS

This file contains functions for interacting with simulated MIPS32
registers and register files

MIPS32 General Purpose Register names and addresses can be found in
GP_REGS and can be interacted with using gpr_write and gpr_read
functions

MIPS32 CP0 Register names and addresses can be found in CP0_REGS.
Currently the read/write operations on these registers is not fully
implemented

CP0 Exception Codes:
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

from os import name
from ctypes import c_int32, c_uint32
from typing import Union

from .memory import MemorySize
from .types import DataType

__VERBOSE__ = 0

GP_REGS = {'$zero': 0, '$at': 1, '$v0': 2, '$v1': 3,
           '$a0': 4, '$a1': 5, '$a2': 6, '$a3': 7,
           '$t0': 8, '$t1': 9, '$t2': 10, '$t3': 11,
           '$t4': 12, '$t5': 13, '$t6': 14, '$t7': 15,
           '$s0': 16, '$s1': 17, '$s2': 18, '$s3': 19,
           '$s4': 20, '$s5': 21, '$s6': 22, '$s7': 23,
           '$t8': 24, '$t9': 25, '$k0': 26, '$k1': 27,
           '$gp': 28, '$sp': 29, '$fp': 30, '$ra': 31}

CP0_REGS = {'$8': 8, '$12': 12, '$13': 13, '$14': 14}

__gp_register_file = {addr: 0 for addr in GP_REGS.values()}
__cp0_register_file = {addr: 0 for addr in CP0_REGS.values()}
pc = 0


def is_register(name: str) -> bool:
    """
    Returns true if name is a valid register name

    Parameters
    ----------
    name : str
        name of register to test

    Returns
    -------
    bool
        True if name is a register name, False otherwise
    """
    return name in GP_REGS or name in CP0_REGS

def get_addr(name: str) -> int:
    """
    Returns the address of a register by name

    Parameters
    ----------
    name : str
        name of register to get address of

    Returns
    -------
    int
        Address of register or None if name is not a valid register name
    """

    if name in GP_REGS: return GP_REGS[name]
    if name in CP0_REGS: return CP0_REGS[name]
    return None

def gpr_write(reg: Union[int, str], val: int) -> None:
    """
    Write a value into a General Purpose Register

    Parameters
    ----------
    reg : int, str
        The register to write a value to.
        Can be address of reg or string name
    val : int
        The value to be written
    """
    global __gp_register_file
    if type(reg) == str:
        if not reg in GP_REGS:
            raise ValueError('Invalid Register name {}'.format(reg))
        reg = GP_REGS[reg]
    if not reg in __gp_register_file:
        raise ValueError('Invalid Register address {}'.format(reg))
    if not DataType.MIN_SINT32 <= val <= DataType.MAX_UINT32:
        raise ValueError('Invalid val {}'.format(val))
    # Use c_uint32 to ensure all values stored in the GPR RF 
    # are unsigned 32 bit integers
    __gp_register_file[reg] = c_uint32(val).value


def gpr_read(reg: Union[int, str], signed=False) -> int:
    """
    Return the value inside reg

    Parameters
    ----------
    reg : int, str
        The register to read.
        Can be address of reg or string name
    """
    if type(reg) == str:
        if not reg in GP_REGS:
            raise ValueError('Invalid Register name {}'.format(reg))
        reg = GP_REGS[reg]
    if not reg in __gp_register_file:
        raise ValueError('Invalid Register address {}'.format(reg))
    if signed:
        # Return value as signed 32-bit integer
        return c_int32(__gp_register_file[reg]).value
    return __gp_register_file[reg]


def increment_pc():
    """
    Shortcut for incrementing the PC register by a word
    """
    global pc
    pc += MemorySize.WORD_LENGTH_BYTES


def gpr_dump(radix=int) -> dict:
    """
    Dump the current state of the GP Register File

    Parameters
    ----------
    radix : int, optional
        The radix used to show values in memory
        (bin, int, hex)

    Returns
    -------
    dict
        A Dictionary of all modified addresses in the following
        format

        {addr: val}
    """
    global pc
    formatting = {int: '{}', hex: '0x{:08x}', bin: '{:032b}'}
    dumped = {}
    for name, addr in GP_REGS.items():
        dumped[name] = formatting[radix].format(c_int32(__gp_register_file[addr]).value)
    dumped['PC'] = pc
    return dumped