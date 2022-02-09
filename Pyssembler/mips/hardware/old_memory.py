"""MIPS32 MEMORY

This file contains functions for interacting with simulated 32-bit memory.

Memory is implemented as a dictionary where each key is a 32-bit address 
that maps to a byte value. The dictionary is initially empty to save space. 
Each time a value is written the appropriate addresses and byte values are 
stored in the dictionary. Trying to read a value from an address that has not
been initialized will return 0 since this logic would be undefined behaviour
in MIPS architecture. The current state of memory can be dumped, though the dump
will only contain memory addresses that have been written to.

All bytes are stored as unsigned 8-bit integers (BYTES) and can be read back
as signed or unsigned.

"""

import json
import os.path
from ctypes import c_int32, c_uint32, c_uint16, c_int16, c_int8, c_uint8
from typing import Callable

from .exceptions import *
from .types import DataType, MemorySize, MemorySegment
from .utils import Integer

__MEMORY_CONFIG_FILE__ = os.path.dirname(__file__) + '/memory_config.json'
__verbose__ = 0


def __log(message: str, verbose: int):
    # Shortcut for logging verbose messages
    if __verbose__ >= verbose:
        print('[MEMORY] {message}'.format(message=message))


class MemoryConfig:
    """
    Class that stores memory config
    """
    with open(__MEMORY_CONFIG_FILE__, 'r') as f:
        config = json.load(f)

        # MIPS32 uses 32-bit addresses for memory
        # Memory is broken up into the following sections:

        # memory mapped I/O section
        mmio_base_addr = int(config['MMIO base address'], 16)
        mmio_limit_addr = int(config['MMIO limit address'], 16)
        # kernel data section
        kdata_base_addr = int(config['kdata base address'], 16)
        kdata_limit_addr = int(config['kdata limit address'], 16)
        # kernel text section
        ktext_base_addr = int(config['ktext base address'], 16)
        ktext_limit_addr = int(config['ktext limit address'], 16)
        # stack section
        stack_base_addr = int(config['stack base address'], 16)
        # user text section
        text_base_addr = int(config['text base address'], 16)
        text_limit_addr = int(config['text limit address'], 16)
        # part of user data section reserved for .extern symbols
        extern_base_addr = int(config['extern base address'], 16)
        extern_limit_addr = int(config['extern limit address'], 16)
        # user data section
        data_base_addr = int(config['data base address'], 16)
        # starting heap address
        heap_base_addr = int(config['heap base address'], 16)
        # boundary between stack and heap
        stack_heap_boundary = int(config['stack-heap boundary'], 16)
        # max address user can write to in memory
        user_memory_limit = int(config['user memory limit'], 16)
        # max memory address
        memory_limit = int(config['memory limit'], 16)
        # starting address for $gp
        global_pointer = int(config['global pointer'], 16)
        stack_pointer = int(config['stack pointer'], 16)


__mem = {}  # Represents 32 bit memory
__instr_mem = {}  # Store ProgramLine objects
heap_address = MemoryConfig.heap_base_addr
__observers = []


def add_observer(observer: Callable):
    __observers.append(observer)


def remove_observer(observer: Callable):
    __observers.remove(observer)


def __notify_observers(addr: int, val: int, size: int):
    for observer in __observers:
        observer(addr, val, size)


def is_valid_addr(addr: int) -> bool:
    """
    Returns true if addr is a valid 32 bit memory address

    Parameters
    ----------
    addr : int
        Address to test
    """
    return 0 <= addr <= MemoryConfig.memory_limit


def in_user_memory(addr: int) -> bool:
    """
    Returns true if addr is in user memory, otherwise false

    User memory consists of Text, Static/Dynamic data and Stack memory segments

    Parameters
    ----------
    addr : int
        Address to test
    """
    return MemoryConfig.text_base_addr <= addr < MemoryConfig.ktext_base_addr


def in_MMIO_segment(addr: int) -> bool:
    """
    Returns true if addr is in MMIO memory segment, otherwise false

    Parameters
    ----------
    addr : int
        Address to test
    """
    return MemoryConfig.mmio_base_addr <= addr < MemoryConfig.mmio_limit_addr


def in_kdata_segment(addr: int) -> bool:
    """
    Returns true if addr is in Kernel Data memory segment, otherwise false

    Parameters
    ----------
    addr : int
        Address to test
    """
    return MemoryConfig.kdata_base_addr <= addr < MemoryConfig.kdata_limit_addr


def in_ktext_segment(addr: int) -> bool:
    """
    Returns true if addr is in Kernel Text memory segment, otherwise false

    Parameters
    ----------
    addr : int
        Address to test
    """
    return MemoryConfig.ktext_base_addr <= addr < MemoryConfig.ktext_limit_addr


def in_stack_segment(addr: int) -> bool:
    """
    Returns true if addr is in Stack memory segment, otherwise false

    Parameters
    ----------
    addr : int
        Address to test
    """
    return MemoryConfig.stack_base_addr >= addr > MemoryConfig.stack_heap_boundary


def in_text_segment(addr: int) -> bool:
    """
    Returns true if addr is in User Text memory segment, otherwise false

    Parameters
    ----------
    addr : int
        Address to test
    """
    return MemoryConfig.text_base_addr <= addr < MemoryConfig.text_limit_addr


def in_extern_segment(addr: int) -> bool:
    """
    Returns true if addr is in Extern memory segment, otherwise false

    Extern memory is located in the lower Static Data memory segment

    Parameters
    ----------
    addr : int
        Address to test
    """
    return MemoryConfig.extern_base_addr <= addr < MemoryConfig.extern_limit_addr


def in_data_segment(addr: int) -> bool:
    """
    Returns true if addr is in User Data memory segment, otherwise false

    Parameters
    ----------
    addr : int
        Address to test
    """
    return MemoryConfig.data_base_addr <= addr < MemoryConfig.stack_heap_boundary


def is_aligned(addr: int, alignment: int) -> bool:
    """
    Returns true if addr is naturally aligned with alignment value

    An address is aligned if addr % alignment == 0

    Parameters
    ----------
    addr : int
        Address to be tested
    alignment : int
        Values addr must be aligned with
    """
    return addr % (alignment // MemorySize.BYTE) == 0


def __write_bytes(addr: int, val: int, num_bytes: int) -> None:
    """
    Helper function for writing an integer value into memory byte by byte
    """
    for i in range(0, num_bytes):
        write_addr = addr + i
        if not is_valid_addr(write_addr):
            raise AddressErrorException(
                'Invalid Address', MIPSExceptionCodes.ADDRS, write_addr)
        byte_val = c_uint8(Integer.get_byte(val, num_bytes - i - 1)).value
        __log('Writing {} into MEM[{}]'.format(byte_val, write_addr), 2)
        __mem[write_addr] = byte_val


def write(addr: int, val: int, size: int) -> None:
    """
    Write a value into 32 bit memory

    Address must be naturally aligned with size

    Parameters
    ----------
    addr : int
        Address to start writing at
    val : int
        Value to be written into memory
    size : int
        Size of value, must be BYTE, HWORD, or WORD 
    """
    __log('Writing {} ({} bits) into MEM[{}]'.format(val, size, addr), 1)
    if not is_aligned(addr, size):
        # raise MemoryError('Address is not naturally aligned')
        raise AddressErrorException(
            'Address is not naturally aligned', MIPSExceptionCodes.ADDRS, addr)
    if not size in (MemorySize.BYTE, MemorySize.HWORD, MemorySize.WORD):
        raise ValueError('Invalid data size: {} bits'.format(size))
    num_bytes = size // MemorySize.BYTE
    if in_stack_segment(addr):
        # Attempting to write to stack, since the stack grows downwards we need
        # to get the lower address of the range we will write to
        addr = addr - (num_bytes) + 1
    __write_bytes(addr, val, num_bytes)
    __notify_observers(addr, val, size)


def write_instruction(addr: int, encoding: int, instruction) -> None:
    """
    Write an instruction into memory

    Address must be aligned on a word boundary

    Parameters
    ----------
    addr : int
        Address to write instruction to
    encoding : int
        Encoded instruction
    instruction : ProgramLine
        Instruction object 
    """
    if not in_text_segment(addr) or in_ktext_segment(addr):
        raise AddressErrorException(
            'Cannot write instruction outside text/ktext segment',
            MIPSExceptionCodes.ADDRS, addr)

    write(addr, encoding, MemorySize.WORD)
    __instr_mem[addr] = instruction


# These functions are for Read/Write operations on the sim memory


def __read_bytes(addr: int, num_bytes: int, signed=False) -> int:
    """
    Reads bytes from memory starting at addr

    Parameters
    ----------
    addr : int
        Address to start reading from
    num_bytes : int
        Number of bytes to read
    signed : bool
        If true, return integer as signed

    Returns
    -------
    int
        resulting integer read from bytes
    """

    __log('Reading {} bytes from memory'.format(num_bytes), 2)
    res = 0
    sa = (num_bytes - 1) * MemorySize.BYTE
    for i in range(0, num_bytes):
        read_addr = addr + i
        if not is_valid_addr(read_addr):
            raise AddressErrorException(
                'Invalid address', MIPSExceptionCodes.ADDRL, read_addr)
        # res = res | (__mem[read_addr] << sa)
        res = res | (__mem.get(read_addr, 0) << sa)
        sa -= MemorySize.BYTE
    if signed:
        if num_bytes == MemorySize.BYTE_LENGTH_BYTES:
            return c_int8(res).value
        if num_bytes == MemorySize.HWORD_LENGTH_BYTES:
            return c_int16(res).value
        if num_bytes == MemorySize.WORD_LENGTH_BYTES:
            return c_int32(res).value
    return res


def read_instruction(addr: int) -> object:
    """
    Get an instruction object from memory
    """
    if not is_aligned(addr, MemorySize.WORD):
        raise AddressErrorException(
            'Address is not aligned on word boundary', MIPSExceptionCodes.ADDRS, addr)
    if not in_text_segment(addr) and not in_ktext_segment(addr):
        raise AddressErrorException(
            'Cannot read instruction outside text/ktext segment',
            MIPSExceptionCodes.ADDRS, addr)
    return __instr_mem.get(addr, None)


def read_word(addr: int, signed=False) -> int:
    """
    Read a word from memory starting at addr

    Parameters
    ----------
    addr : int
        Address to start reading from
    signed : bool, optional
        If True, read value from memory as signed

    Returns
    -------
    int
        Value read from memory 
    """
    if not is_aligned(addr, MemorySize.WORD):
        raise AddressErrorException(
            'Address is not aligned on word boundary', MIPSExceptionCodes.ADDRL, addr)
    if in_stack_segment(addr):
        # Address is in stack segment, read value backwards since
        # stack addresses grow downwards
        addr = addr - MemorySize.WORD_LENGTH_BYTES + 1
    return __read_bytes(addr, MemorySize.WORD_LENGTH_BYTES, signed=signed)


def read_hword(addr: int, signed=False) -> int:
    """
    Read a half word from memory starting at addr

    Parameters
    ----------
    addr : int
        Address to start reading from
    signed : bool, optional
        If True, read value from memory as signed

    Returns
    -------
    int
        Value read from memory 
    """

    if not is_aligned(addr, MemorySize.WORD):
        raise AddressErrorException(
            'Address is not aligned on half-word boundary', MIPSExceptionCodes.ADDRL, addr)
    if in_stack_segment(addr):
        # Address is in stack segment, read value backwards since
        # stack addresses grow downwards
        addr = addr - MemorySize.HWORD_LENGTH_BYTES + 1
    return __read_bytes(addr, MemorySize.HWORD_LENGTH_BYTES, signed=signed)


def read_byte(addr: int, signed=False) -> int:
    """
    Read a byte from memory starting at addr

    Parameters
    ----------
    addr : int
        Address to start reading from
    signed : bool, optional
        If True, read value from memory as signed

    Returns
    -------
    int
        Value read from memory 
    """
    if not is_valid_addr(addr):
        # raise MemoryError('Address {} out of bounds'.format(addr))
        raise AddressErrorException(
            'Invalid address', MIPSExceptionCodes.ADDRL, addr)
    val = __mem.get(addr, 0)
    if signed:
        return c_int8(val).value
    return val


def allocate_heap_bytes(num_bytes: int) -> int:
    global heap_address
    if num_bytes < 0:
        raise ValueError('Cannot allocate negative bytes: {}'.format(num_bytes))
    new_addr = heap_address + num_bytes
    if not is_aligned(new_addr, MemorySize.WORD):
        new_addr = new_addr + (4 - new_addr % 4)
    if not in_data_segment(new_addr):
        raise AddressErrorException('Heap overflowed from data segment', new_addr)
    heap_address, old_address = new_addr, heap_address
    return old_address


# These functions are for exporting contents of memory

def get_modified_addresses() -> list:
    """
    Get a list of modified addresses

    Since memory is simulated as a python dictionary,
    all addresses that are modified (written to) will be a key
    in the dictionary

    Returns
    -------
    list
        A list of all modified addresses
    """

    return list(__mem.keys())


def get_segment(addr: int) -> MemorySegment:
    if in_text_segment(addr):
        return MemorySegment.TEXT
    if in_ktext_segment(addr):
        return MemorySegment.KTEXT
    if in_data_segment(addr):
        return MemorySegment.DATA
    if in_kdata_segment(addr):
        return MemorySegment.KDATA
    if in_extern_segment(addr):
        return MemorySegment.EXTERN
    if in_MMIO_segment(addr):
        return MemorySegment.MMIO
    raise ValueError(f'Invalid address {addr}')


def dump(radix=int) -> dict:
    """
    Dump the current state of memory

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

        {addr: [addr +0, addr+1, addr+2, addr+3]}
    """
    formatting = {int: '{}', hex: '0x{:02x}', bin: '{:08b}'}
    if not radix in formatting:
        raise ValueError('Invalid radix type')
    dumped = {seg: {} for seg in MemorySegment}
    non_aligned = []
    for addr in __mem:
        if is_aligned(addr, MemorySize.WORD):
            seg = get_segment(addr)
            dumped[seg][addr] = []
            for i in range(MemorySize.WORD_LENGTH_BYTES):
                val = formatting[radix].format(__mem.get(addr + i, 0), 2)
                dumped[seg][addr].append(val)
        else:
            non_aligned.append(addr)
    for addr in non_aligned:
        seg = get_segment(addr)
        for a in (addr - 1, addr - 2, addr - 3):
            if is_aligned(a, MemorySize.WORD) and not a in dumped[seg]:
                dumped[seg][a] = []
                for i in range(MemorySize.WORD_LENGTH_BYTES):
                    val = formatting[radix].format(__mem.get(a + i, 0), 2)
                    dumped[seg][a].append(val)
                    break
    return dumped