from ctypes import c_int32, c_int16, c_int8, c_uint8

from ..mips_exceptions import *
from . import integer


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


class MIPSMemory:
    """
    Simulated MIPS32 memory

    MIPS32 allows up to 4 GB (32-bit addresses) of addressable memory
    for a program. This memory is broken into multiple segments as shown
    in the below diagram.

    An important note to make is how the program data segment is managed. It
    is broken up into 4 main sub-segments:
    - Program Data declared using the .extern directive (static)
    - Program Data declared using the .data directive (static)
    - Heap (dynamic)
    - Stack (dynamic)

    By convention the Stack is used to save values across function calls. This
    segment is unique because it's addressing space grows downwards.
    The Heap is used to save user data during runtime. The user must use
    a system call to allocate heap memory. This segments addressing space
    grows upwards.

    It is possible for either of these segments to grow into each other's space,
    causing corrupted memory. This class implements a Stack-Heap boundary that
    protects against this case. This can be customized or disabled.
    ┌──────────────────────┐
    │Memory Mapped IO      │
    ├──────0xffff0000──────┤
    │Kernel Data           │
    ├──────0x90000000──────┤
    │Kernel Text           │
    ├──────0x7ffffe00──────┤
    │Stack                 │
    ├──────────┬───────────┤
    │          │Grows Down │
    │          ▼           │
    │                      │
    │          ▲           │
    │          │Grows Up   │
    ├──────────┴───────────┤
    │Heap                  │
    ├──────0x10040000──────┤
    │Program Data (.data)  │
    ├──────0x10010000──────┤
    │Program Data (.extern)│
    ├──────0x10000000──────┤
    │Program Text          │
    ├──────0x00400000──────┤
    │Reserved              │
    └──────────────────────┘
    """

    # Default Memory Segments
    MEMORY_LIMIT = 0xffffffff
    MMIO_LIMIT_ADDRESS = 0xffff0010
    MMIO_BASE_ADDRESS = 0xffff0000
    KDATA_LIMIT_ADDRESS = 0xffff0000
    KDATA_BASE_ADDRESS = 0x90000000
    KTEXT_LIMIT_ADDRESS = 0x90000000
    KTEXT_BASE_ADDRESS = 0x80000000
    USER_MEMORY_LIMIT = 0x7fffffff
    STACK_BASE_ADDRESS = 0x7ffffffc
    STACK_HEAP_BOUNDARY = 0x40000000
    HEAP_BASE_ADDRESS = 0x10040000
    DATA_BASE_ADDRESS = 0x10010000
    EXTERN_LIMIT_ADDRESS = 0x10010000
    EXTERN_BASE_ADDRESS = 0x10000000
    TEXT_LIMIT_ADDRESS = 0x0ffffffc
    TEXT_BASE_ADDRESS = 0x00400000

    GLOBAL_POINTER = 0x10008000
    STACK_POINTER = 0x7fffeffc

    # Memory Segment
    TEXT_SEGMENT = 'text'
    DATA_SEGMENT = 'data'
    KTEXT_SEGMENT = 'ktext'
    KDATA_SEGMENT = 'kdata'
    EXTERM_SEGMENT = 'extern'
    MMIO_SEGMENT = 'mmio'

    def __init__(self):
        super().__init__()
        self.__mem = {}
        self.__instr_mem = {}
        self.heap_address = self.HEAP_BASE_ADDRESS

    @property
    def memory(self):
        return self.__mem.copy()

    def write(self, addr: int, val: int, size: int) -> None:
        """
        Write a value into 32-bit memory

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
        if not self.is_aligned(addr, size):
            # raise MemoryError('Address is not naturally aligned')
            raise AddressErrorException(
                'Address is not naturally aligned', MIPSExceptionCodes.ADDRS, addr)
        if size not in (MemorySize.BYTE, MemorySize.HWORD, MemorySize.WORD):
            raise ValueError('Invalid data size: {} bits'.format(size))
        num_bytes = size // MemorySize.BYTE
        if self.in_stack_segment(addr):
            # Attempting to write to stack, since the stack grows downwards we need
            # to get the lower address of the range we will write to
            addr = addr - num_bytes + 1
        self.__write_bytes(addr, val, num_bytes)

    def write_instruction(self, addr: int, encoding: int, instruction) -> None:
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
        if not self.in_text_segment(addr) or self.in_ktext_segment(addr):
            raise AddressErrorException(
                'Cannot write instruction outside text/ktext segment',
                MIPSExceptionCodes.ADDRS, addr)

        self.write(addr, encoding, MemorySize.WORD)
        self.__instr_mem[addr] = instruction

    def read_word(self, addr: int, signed=False) -> int:
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
        if not self.is_aligned(addr, MemorySize.WORD):
            raise AddressErrorException(
                'Address is not aligned on word boundary', MIPSExceptionCodes.ADDRL, addr)
        if self.in_stack_segment(addr):
            # Address is in stack segment, read value backwards since
            # stack addresses grow downwards
            addr = addr - MemorySize.WORD_LENGTH_BYTES + 1
        return self.__read_bytes(addr, MemorySize.WORD_LENGTH_BYTES, signed=signed)

    def read_hword(self, addr: int, signed=False) -> int:
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

        if not self.is_aligned(addr, MemorySize.WORD):
            raise AddressErrorException(
                'Address is not aligned on half-word boundary', MIPSExceptionCodes.ADDRL, addr)
        if self.in_stack_segment(addr):
            # Address is in stack segment, read value backwards since
            # stack addresses grow downwards
            addr = addr - MemorySize.HWORD_LENGTH_BYTES + 1
        return self.__read_bytes(addr, MemorySize.HWORD_LENGTH_BYTES, signed=signed)

    def read_byte(self, addr: int, signed=False) -> int:
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
        if not self.is_valid_addr(addr):
            # raise MemoryError('Address {} out of bounds'.format(addr))
            raise AddressErrorException(
                'Invalid address', MIPSExceptionCodes.ADDRL, addr)
        val = self.__mem.get(addr, 0)
        if signed:
            return c_int8(val).value
        return val

    def read_instruction(self, addr: int) -> object:
        """
        Get an instruction object from memory
        """
        if not self.is_aligned(addr, MemorySize.WORD):
            raise AddressErrorException(
                'Address is not aligned on word boundary', MIPSExceptionCodes.ADDRS, addr)
        if not self.in_text_segment(addr) and not self.in_ktext_segment(addr):
            raise AddressErrorException(
                'Cannot read instruction outside text/ktext segment',
                MIPSExceptionCodes.ADDRS, addr)
        return self.__instr_mem.get(addr, None)

    def __write_bytes(self, addr: int, val: int, num_bytes: int) -> None:
        """
        Helper function for writing an integer value into memory byte by byte
        """
        for i in range(0, num_bytes):
            write_addr = addr + i
            if not self.is_valid_addr(write_addr):
                raise AddressErrorException(
                    'Invalid Address', MIPSExceptionCodes.ADDRS, write_addr)
            byte_val = c_uint8(integer.get_byte(val, num_bytes - i - 1)).value
            self.__mem[write_addr] = byte_val
            boundary = self.get_word_boundary(addr)
            word_val = self.read_word(boundary)
            byte_vals = [self.read_byte(b) for b in range(boundary, self.get_word_boundary(addr, upper=True))]

    def __read_bytes(self, addr: int, num_bytes: int, signed=False) -> int:
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

        res = 0
        sa = (num_bytes - 1) * MemorySize.BYTE
        for i in range(0, num_bytes):
            read_addr = addr + i
            if not self.is_valid_addr(read_addr):
                raise AddressErrorException(
                    'Invalid address', MIPSExceptionCodes.ADDRL, read_addr)
            # res = res | (__mem[read_addr] << sa)
            res = res | (self.__mem.get(read_addr, 0) << sa)
            sa -= MemorySize.BYTE
        if signed:
            if num_bytes == MemorySize.BYTE_LENGTH_BYTES:
                return c_int8(res).value
            if num_bytes == MemorySize.HWORD_LENGTH_BYTES:
                return c_int16(res).value
            if num_bytes == MemorySize.WORD_LENGTH_BYTES:
                return c_int32(res).value
        return res

    def allocate_heap_bytes(self, num_bytes: int) -> int:
        if num_bytes < 0:
            raise ValueError('Cannot allocate negative bytes: {}'.format(num_bytes))
        new_addr = self.heap_address + num_bytes
        if not self.is_aligned(new_addr, MemorySize.WORD):
            new_addr = new_addr + (4 - new_addr % 4)
        if not self.in_data_segment(new_addr):
            raise AddressErrorException(
                'Heap overflowed from data segment',
                new_addr,
                MIPSExceptionCodes.ADDRS
            )
        heap_address, old_address = new_addr, self.heap_address
        return old_address

    def get_modified_addresses(self) -> list:
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

        return list(self.__mem.keys())

    def get_segment(self, addr: int) -> str:
        if self.in_text_segment(addr):
            return self.TEXT_SEGMENT
        if self.in_ktext_segment(addr):
            return self.KTEXT_SEGMENT
        if self.in_data_segment(addr):
            return self.DATA_SEGMENT
        if self.in_kdata_segment(addr):
            return self.KDATA_SEGMENT
        if self.in_extern_segment(addr):
            return self.EXTERM_SEGMENT
        if self.in_MMIO_segment(addr):
            return self.MMIO_SEGMENT
        raise ValueError(f'Invalid address {addr}')

    def is_valid_addr(self, addr: int) -> bool:
        """
        Returns true if addr is a valid 32 bit memory address

        Parameters
        ----------
        addr : int
            Address to test
        """
        return 0 <= addr <= self.MEMORY_LIMIT

    def in_user_memory(self, addr: int) -> bool:
        """
        Returns true if addr is in user memory, otherwise false

        User memory consists of Text, Static/Dynamic data and Stack memory segments

        Parameters
        ----------
        addr : int
            Address to test
        """
        return self.TEXT_BASE_ADDRESS <= addr < self.KTEXT_BASE_ADDRESS

    def in_MMIO_segment(self, addr: int) -> bool:
        """
        Returns true if addr is in MMIO memory segment, otherwise false

        Parameters
        ----------
        addr : int
            Address to test
        """
        return self.MMIO_BASE_ADDRESS <= addr < self.MMIO_LIMIT_ADDRESS

    def in_kdata_segment(self, addr: int) -> bool:
        """
        Returns true if addr is in Kernel Data memory segment, otherwise false

        Parameters
        ----------
        addr : int
            Address to test
        """
        return self.KDATA_BASE_ADDRESS <= addr < self.KDATA_LIMIT_ADDRESS

    def in_ktext_segment(self, addr: int) -> bool:
        """
        Returns true if addr is in Kernel Text memory segment, otherwise false

        Parameters
        ----------
        addr : int
            Address to test
        """
        return self.KTEXT_BASE_ADDRESS <= addr < self.KTEXT_LIMIT_ADDRESS

    def in_stack_segment(self, addr: int) -> bool:
        """
        Returns true if addr is in Stack memory segment, otherwise false

        Parameters
        ----------
        addr : int
            Address to test
        """
        return self.STACK_BASE_ADDRESS >= addr > self.STACK_HEAP_BOUNDARY

    def in_text_segment(self, addr: int) -> bool:
        """
        Returns true if addr is in User Text memory segment, otherwise false

        Parameters
        ----------
        addr : int
            Address to test
        """
        return self.TEXT_BASE_ADDRESS <= addr < self.TEXT_LIMIT_ADDRESS

    def in_extern_segment(self, addr: int) -> bool:
        """
        Returns true if addr is in Extern memory segment, otherwise false

        Extern memory is located in the lower Static Data memory segment

        Parameters
        ----------
        addr : int
            Address to test
        """
        return self.EXTERN_BASE_ADDRESS <= addr < self.EXTERN_LIMIT_ADDRESS

    def in_data_segment(self, addr: int) -> bool:
        """
        Returns true if addr is in User Data memory segment, otherwise false

        Parameters
        ----------
        addr : int
            Address to test
        """
        return self.DATA_BASE_ADDRESS <= addr <= self.STACK_BASE_ADDRESS

    def is_aligned(self, addr: int, alignment: int) -> bool:
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

    def get_word_boundary(self, addr: int, upper=False):
        """
        Returns the upper/lower word boundary of an address

        For example, 3 would return 0 or 4

        Parameters
        ----------
        addr: int
            The address to get the word boundary of
        upper: bool, default=False
            Returns the upper boundary if True, otherwise lower boundary
        """
        if not self.is_valid_addr(addr):
            raise ValueError('Cannot get boundary of invalid address')
        end = addr + 4 if upper else addr - 4
        inc = 1 if upper else -1
        for i in range(addr, end, inc):
            if self.is_aligned(i, MemorySize.WORD):
                return i

    def reset(self, *segments):
        """
        Erases all of simulated memory

        Or pass specific MemorySegments to be deleted
        """
        if len(segments) == 0:
            # Default case, clear all of memory
            self.__mem.clear()
            return

        self.__mem = {a: v for a, v in self.__mem.items() if self.get_segment(a) not in segments}

    def dump(self, radix=int) -> dict:
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
        if radix not in formatting:
            raise ValueError('Invalid radix type')
        dumped = {
            self.TEXT_SEGMENT: {},
            self.DATA_SEGMENT: {},
            self.KTEXT_SEGMENT: {},
            self.KDATA_SEGMENT: {},
            self.EXTERM_SEGMENT: {},
            self.MMIO_SEGMENT: {}
        }
        non_aligned = []
        for addr in self.__mem:
            if self.is_aligned(addr, MemorySize.WORD):
                seg = self.get_segment(addr)
                dumped[seg][addr] = []
                for i in range(MemorySize.WORD_LENGTH_BYTES):
                    val = formatting[radix].format(self.__mem.get(addr + i, 0), 2)
                    dumped[seg][addr].append(val)
            else:
                non_aligned.append(addr)
        for addr in non_aligned:
            seg = self.get_segment(addr)
            for a in (addr - 1, addr - 2, addr - 3):
                if self.is_aligned(a, MemorySize.WORD) and not a in dumped[seg]:
                    dumped[seg][a] = []
                    for i in range(MemorySize.WORD_LENGTH_BYTES):
                        val = formatting[radix].format(self.__mem.get(a + i, 0), 2)
                        dumped[seg][a].append(val)
                        break
        return dumped
