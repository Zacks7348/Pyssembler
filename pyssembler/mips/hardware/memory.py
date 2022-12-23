"""
This file contains classes to simulate MIPS32 memory.

MIPS32 implements a byte-addressable 32-bit flat memory model.
This means that each unique address (0x00000000 - 0xffffffff)
points to a single byte of data. This ends up being around 4GB
of available memory for a single program.

The endianness of simulated memory is determined by `sys.byteorder`

MIPS breaks up a programs memory-space into different segments that fall
into the following main categories:

 - User Space: This is memory accessible by the program.

 - Kernel Space: This is memory reserved for the kernel (operating system
    functions such as exception handling). It is not useable by a program.

 - Reserved: This is memory reserved for the MIPS platform and is not
    useable by a program.

Below is a more-detailed breakdown of the MIPS32 memory model:
                    ┌──────────────────────┐
                    │Memory Mapped IO      │
                    ├──────────────────────┤
                    │Kernel Data           │
                    ├──────────────────────┤
                    │Kernel Text           │
                    ├──────────────────────┤
                    │Stack                 │
                    ├──────────┬───────────┤
                    │          │Grows Down │
                    │          ▼           │
                    │                      │
                    │          ▲           │
                    │          │Grows Up   │
                    ├──────────┴───────────┤
                    │Heap                  │
                    ├──────────────────────┤
                    │User Data (.data)     │
                    ├──────────────────────┤
                    │User Data (.extern)   │
                    ├──────────────────────┤
                    │User Text             │
                    ├──────────────────────┤
                    │Reserved              │
                    └──────────────────────┘

An important note to make is how the program data segment is managed. It
    is broken up into 4 main sub-segments:
    - User Data declared using the .extern directive (static)
    - User Data declared using the .data directive (static)
    - Heap (dynamic)
    - Stack (dynamic)

    By convention the Stack is used to save values across function calls. This
    segment is unique because it's addressing space grows downwards.
    The Heap is used to save user data during runtime. The user must use
    a system call to allocate heap memory. This segments addressing space
    grows upwards.

    It is possible for either of these segments to grow into each other's space,
    causing corrupted memory. The `Memory` class implements a Stack-Heap boundary
    that protects against this case. This can be customized or disabled.
"""
import typing

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

    Memory is implemented as a dictionary that maps addresses to byte values.
    Addresses that are not in the dictionary are assumed to contain a byte
    value 0. This allows for dynamically growing the internal dictionary only
    for addresses that have explicitly been written to.
    """

    # Default Memory Segments
    MEMORY_LIMIT = 0x100000000
    DEFAULT_MMIO_START = 0xffff0000
    DEFAULT_KERNEL_DATA_START = 0x90000000
    DEFAULT_KERNEL_TEXT_START = 0x7ffffe00
    DEFAULT_STACK_START = 0x7ffffdfc
    DEFAULT_HEAP_STACK_BOUNDARY = 0x40000000
    DEFAULT_HEAP_START = 0x10040000
    DEFAULT_USER_DATA_START = 0x10000000
    DEFAULT_EXTERN_DATA_START = 0x10000000
    DEFAULT_USER_TEXT_START = 0x00400000
    MEMORY_START = 0x00000000

    # Memory Segment
    MMIO_SEGMENT = 'mmio'
    KERNEL_DATA_SEGMENT = 'kdata'
    KERNEL_TEXT_SEGMENT = 'ktext'
    STACK_SEGMENT = 'stack'
    HEAP_SEGMENT = 'heap'
    USER_DATA_SEGMENT = 'data'
    EXTERM_SEGMENT = 'extern'
    USER_TEXT_SEGMENT = 'text'
    RESERVED_SEGMENT = 'reserved'

    def __init__(self, **kwargs):
        super().__init__()
        self.__init_segments(**kwargs)

        # Configuration flags
        self._force_align: bool = kwargs.pop('force_align', False)
        self._enable_heap_stack_boundary: bool = kwargs.pop('enable_heap_stack_boundary', True)

        self.mem = {}
        self.instr_mem = {}

        self._heap_address = self.heap_start

    @property
    def heap_address(self):
        return self._heap_address

    @property
    def force_align(self):
        return self._force_align

    def __init_segments(self, **kwargs):
        """
        Initialize the segment boundaries
        """
        self.mmio_start = kwargs.pop('mmio', self.DEFAULT_MMIO_START)
        self.kernel_data_start = kwargs.pop('kernel_data', self.DEFAULT_KERNEL_DATA_START)
        self.kernel_text_start = kwargs.pop('kernel_text', self.DEFAULT_KERNEL_TEXT_START)
        self.stack_start = kwargs.pop('stack', self.DEFAULT_STACK_START)
        self.heap_stack_boundary = kwargs.pop('heap_stack_boundary', self.DEFAULT_HEAP_STACK_BOUNDARY)
        self.heap_start = kwargs.pop('heap', self.DEFAULT_HEAP_START)
        self.user_data_start = kwargs.pop('user_data', self.DEFAULT_USER_DATA_START)
        self.extern_data_start = kwargs.pop('extern_data', self.DEFAULT_EXTERN_DATA_START)
        self.user_text_start = kwargs.pop('user_text', self.DEFAULT_USER_TEXT_START)

    def is_heap_stack_boundary_enabled(self):
        return self._enable_heap_stack_boundary

    def enable_heap_stack_boundary(self):
        self._enable_heap_stack_boundary = True

    def disable_heap_stack_boundary(self):
        self._enable_heap_stack_boundary = False

    def clear(self, *segments):
        """
        Clear the contents of memory
        """
        if not segments:
            self.mem.clear()
            self.instr_mem.clear()

        for addr in list(self.mem.keys()):
            addr_segment = self.get_segment(addr)
            if addr_segment in segments:
                self.mem.pop(addr)

            if self.USER_TEXT_SEGMENT in segments:
                self.instr_mem.clear()

    def _read_bytes(self, addr: int, num_bytes: int, signed=False):
        """
        Helper function to read bytes from memory starting at addr
        """

    def _write_bytes(self, addr: int, int_bytes: typing.List[int], downwards=False):
        """
        Helper function to write bytes to memory. Bytes are written
        """

    def allocate_heap_bytes(self, num_bytes: int) -> int:
        if num_bytes < 0:
            raise ValueError(f'Cannot allocate negative bytes: {num_bytes}')
        new_addr = self._heap_address + num_bytes
        if not self.in_heap_segment(new_addr):
            raise AddressErrorException(
                'Heap overflowed',
                new_addr,
                MIPSExceptionCodes.ADDRS
            )
        self._heap_address, old_addr = new_addr, self._heap_address
        return old_addr

    def get_segment(self, addr: int) -> str:
        """
        Return the memory segment addr falls in
        """
        if not self.is_valid_address(addr):
            raise ValueError('Invalid address {addr}')

        if self.in_mmio_segment(addr):
            return self.MMIO_SEGMENT
        if self.in_kernel_data_segment(addr):
            return self.KERNEL_DATA_SEGMENT
        if self.in_kernel_text_segment(addr):
            return self.KERNEL_TEXT_SEGMENT
        if self.in_stack_segment(addr):
            return self.STACK_SEGMENT
        if self.in_heap_segment(addr):
            return self.HEAP_SEGMENT
        if self.in_user_data_segment(addr):
            return self.USER_DATA_SEGMENT
        if self.in_extern_data_segment(addr):
            return self.EXTERM_SEGMENT
        if self.in_user_text_segment(addr):
            return self.USER_TEXT_SEGMENT
        if self.in_reserved_memory(addr):
            return self.RESERVED_SEGMENT

    def is_aligned(self, addr: int, alignment: int) -> bool:
        """
        Returns True if addr is naturally aligned with the data size.

        Halfword accesses are aligned on even byte boundary (0, 2, 4...)
        Word accesses are aligned on a byte boundary divisible by four (0, 4, 8...)
        """
        return addr % (alignment // MemorySize.BYTE) == 0

    def is_valid_address(self, addr: int) -> bool:
        """
        Returns True if addr is a valid 32-bit memory address
        """
        if type(addr) is not int:
            return False

        return self.MEMORY_START <= addr < self.MEMORY_LIMIT

    def in_user_memory(self, addr: int) -> bool:
        """
        Returns True if addr is a valid memory address located in the User
        memory segments
        """
        return self.in_user_text_segment(addr) or \
               self.in_extern_data_segment(addr) or \
               self.in_user_data_segment(addr) or \
               self.in_heap_segment(addr) or \
               self.in_stack_segment(addr)

    def in_kernel_memory(self, addr: int) -> bool:
        """
        Returns True if addr is a valid memory address located in the Kernel
        memory segments
        """
        return self.in_kernel_text_segment(addr) or self.in_kernel_data_segment(addr)

    def in_mmio_segment(self, addr: int) -> bool:
        """
        Returns True if addr is a valid memory address located in the MMIO
        memory segment
        """
        return self.is_valid_address(addr) and \
               (self.mmio_start <= addr < self.MEMORY_LIMIT)

    def in_kernel_data_segment(self, addr: int) -> bool:
        """
        Returns True if addr is a valid memory address located in the Kernel
        Data memory segment
        """
        return self.is_valid_address(addr) and \
               (self.kernel_data_start <= addr < self.mmio_start)

    def in_kernel_text_segment(self, addr: int) -> bool:
        """
        Returns True if addr is a valid memory address located in the Kernel
        Text memory segment
        """
        return self.is_valid_address(addr) and \
               (self.kernel_text_start <= addr < self.kernel_data_start)

    def in_stack_segment(self, addr: int) -> bool:
        """
        Returns True if addr is a valid memory address located in the Stack
        memory segment.

        The address is in the Stack if it is below the Stack starting address
        and above the Heap-Stack boundary if enabled, otherwise the Heap starting
        address.
        """
        if not self.is_valid_address(addr):
            return False

        if self.enable_heap_stack_boundary:
            return self.heap_stack_boundary <= addr < self.stack_start

        return self.heap_start <= addr < self.stack_start

    def in_heap_segment(self, addr: int) -> bool:
        """
        Returns True if addr is a valid memory address located in the Heap
        memory segment.

        The address is in the Heap if it is above the Heap starting address
        and below the Heap-Stack boundary if enabled, otherwise the Stack
        starting address
        """
        if not self.is_valid_address(addr):
            return False

        if self.enable_heap_stack_boundary:
            return self.heap_start <= addr < self.heap_stack_boundary

        return self.heap_start <= addr < self.stack_start

    def in_user_data_segment(self, addr: int) -> bool:
        """
        Returns True if addr is a valid memory address located in the User
        Data (.data) memory segment
        """
        return self.is_valid_address(addr) and \
               (self.user_data_start <= addr < self.heap_start)

    def in_extern_data_segment(self, addr: int) -> bool:
        """
        Returns True if addr is a valid memory address located in the User
        Data (.extern) memory segment
        """
        return self.is_valid_address(addr) and \
               (self.extern_data_start <= addr < self.user_data_start)

    def in_user_text_segment(self, addr: int) -> bool:
        """
        Returns True if addr is a valid memory address located in the User
        Text memory segment
        """
        return self.is_valid_address(addr) and \
               (self.user_text_start <= addr < self.extern_data_start)

    def in_reserved_memory(self, addr: int) -> bool:
        """
        Returns True if addr is a valid memory address located in a Reserved
        memory segment
        """
        return self.is_valid_address(addr) and \
               (self.MEMORY_START <= addr < self.user_text_start)
