import json
import os.path
from ctypes import c_int32, c_uint32, c_int8

from .errors import MemoryError
from .types import DataType
from ..utils import Integer

__MEMORY_CONFIG_FILE__ = os.path.dirname(__file__)+'/memory_config.json'
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
        heap_pointer = heap_base_addr
        # boundary between stack and heap
        stack_heap_boundary = int(config['stack-heap boundary'], 16)
        # max address user can write to in memory
        user_memory_limit = int(config['user memory limit'], 16)
        # max memory address
        memory_limit = int(config['memory limit'], 16)
        # starting address for $gp
        global_pointer = int(config['global pointer'], 16)


class MemorySize:
    """
    Stores some useful memory size values
    """
    BIT = 1
    BYTE = 8
    HWORD = 16
    WORD = 32
    WORD_LENGTH_BYTES = WORD // BYTE
    HWORD_LENGTH_BYTES = HWORD // BYTE
    BYTE_LENGTH_BYTES = BYTE // BYTE


__mem = {}  # Represents 32 bit memory


def set_verbose(verbose: int) -> None:
    """
    Set the verbose level for memory actions

    Parameters
    ----------
    verbose : int
        Verbose level (0-None, 1-Basic, 2-All)
    """
    global __verbose__
    if not 0 <= verbose <= 2:
        raise ValueError('Invalid MEM verbose value')
    __verbose__ = verbose

# These are some helper functions for address verification


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


def __write_bytes(addr: int, byte_list) -> None:
    """
    Helper function for writing a list of bytes into memory starting at addr
    """

    for offset, byte in enumerate(byte_list):
        write_addr = addr+offset
        if not is_valid_addr(write_addr):
            raise MemoryError(
                'Address {} is not a valid 32 bit address'.format(write_addr))
        __log('Writing {} into MEM[{}]'.format(byte, write_addr), 2)
        __mem[write_addr] = byte


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
    if not size in (MemorySize.BYTE, MemorySize.HWORD, MemorySize.WORD):
        raise ValueError('Invalid size {}'.format(size))
    if not is_aligned(addr, size):
        raise ValueError('Address is not naturally aligned')
    if not is_valid_addr(addr):
        raise MemoryError('Address {} is out of bounds'.format(addr))
    masks = {MemorySize.WORD: 0xFF000000, MemorySize.HWORD: 0x0000FF00,
             MemorySize.BYTE: 0x000000FF}
    byte_list = []
    for i in range(0, size, MemorySize.BYTE):
        # Get a list of bytes starting at highest bit
        # size-i-BYTE-1 gives us lowest bit of next byte
        # size-i gives us highest bit of next byte
        byte_list.append(Integer.get_bits(
            val, size-i-MemorySize.BYTE, size-i-1))
    if in_stack_segment(addr):
        # Attempting to write to stack, since the stack grows downwards we need
        # to get the higher address of the range we will write to
        addr = addr-len(byte_list)+1
    __write_bytes(addr, byte_list)


# These functions are for Read/Write operations on the sim memory

def __read_bytes(addr: int, num_bytes: int) -> list:
    """
    Reads bytes from memory starting at addr

    Parameters
    ----------
    addr : int
        Address to start reading from
    num_bytes : int
        Number of bytes to read

    Returns
    -------
    list
        List of bytes in the order that they were read
    """

    __log('Reading {} bytes from memory'.format(num_bytes))
    if not is_valid_addr(addr):
        raise MemoryError('Address {} out of range'.format(addr))
    return [__mem.get(addr+i, 0) for i in range(num_bytes)]


def __build_value(byte_list: list, signed=False):
    """
    Given a list of bytes, reconstruct original value

    Parameters
    ----------
    byte_list : list
        List of bytes in big-endian order
    signed : bool
        Flag for reconstructing value as signed/unsigned

    Returns
        Reconstructed int
    """

    if len(byte_list) > 4:
        raise ValueError('Too many bytes for 32 bit value')
    while len(byte_list) < 4:
        # Sign/zero extend to 32 bits
        if signed:
            byte_list.insert(0, DataType.MAX_UINT8)
        else:
            byte_list.insert(0, 0)
    val = 0
    for i, byte in enumerate(byte_list):
        val |= byte << (len(byte_list)-i-1)*MemorySize.BYTE
    if signed:
        return c_int32(val).value
    return val


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

    if in_stack_segment(addr):
        # Address is in stack segment, read value backwards since
        # stack addresses grow downwards
        addr = addr - MemorySize.WORD_LENGTH_BYTES + 1
    return __build_value(__read_bytes(
        addr, MemorySize.WORD_LENGTH_BYTES), signed=signed)


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

    if in_stack_segment(addr):
        # Address is in stack segment, read value backwards since
        # stack addresses grow downwards
        addr = addr - MemorySize.HWORD_LENGTH_BYTES + 1
    return __build_value(__read_bytes(
        addr, MemorySize.HWORD_LENGTH_BYTES), signed=signed)


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
        raise MemoryError('Address {} out of bounds'.format(addr))
    val = __mem.get(addr, 0)
    if signed:
        return c_int8(val).value
    return val


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

        {addr: [val +0, val+1, val+2, val+2]}
    """
    formatting = {int: '{}', hex: '0x{:02x}', bin: '{:08b}'}
    if not radix in formatting:
        raise ValueError('Invalid radix type')
    dumped = {}
    for addr in __mem:
        if addr % 4 == 0:
            dumped[addr] = []
            for i in range(MemorySize.WORD_LENGTH_BYTES):
                val = formatting[radix].format(__mem.get(addr+i, 0), 2)
                dumped[addr].append(val)
    return dumped

