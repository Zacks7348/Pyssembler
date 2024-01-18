from pyssembler.architecture.mips.common.hardware import MIPSMemory, MIPSMemorySegment, MIPSTextMemorySegment
from pyssembler.architecture.mips.common.mips_enums import Segment


class MIPS32MemoryConfig:
    """
    Class that stores memory config
    """

    # Upper Reserved
    upper_reserved_upper_addr = 0xffffffff
    upper_reserved_lower_addr = 0xffff0010

    # memory mapped I/O
    mmio_upper_addr = 0xffff000f
    mmio_lower_addr = 0xffff0000

    # kernel data
    kdata_upper_addr = 0xfffeffff
    kdata_lower_addr = 0x90000000

    # kernel text
    ktext_upper_addr = 0x8fffffff
    ktext_lower_addr = 0x80000000

    # stack
    stack_upper_addr = 0x7fffffff
    stack_lower_addr = 0x40000000

    # Heap
    heap_upper_addr = 0x3fffffff
    heap_lower_addr = 0x10040000

    # User Data
    data_upper_addr = 0x1003ffff
    data_lower_addr = 0x10000000

    # user text
    text_upper_addr = 0x0fffffff
    text_lower_addr = 0x00400000

    # Lower Reserved
    lower_reserved_upper_addr = 0x3fffff
    lower_reserved_lower_addr = 0


class MIPS32Memory(MIPSMemory):
    def __init__(self, config: MIPS32MemoryConfig = None):
        self.config = config or MIPS32MemoryConfig()
        super().__init__()

    def _init_segments(self) -> None:
        # Reserved - Not Implemented
        self._top_reserved = MIPSMemorySegment(
            'Reserved',
            upper_address=self.config.upper_reserved_upper_addr,
            lower_address=self.config.upper_reserved_lower_addr,
            access_level=Segment.KERNEL
        )
        self._register_memory_segment(self._top_reserved)

        # Memory Mapped IO
        self._mmio_segment = MIPSMemorySegment(
            'Memory Managed IO',
            upper_address=self.config.mmio_upper_addr,
            lower_address=self.config.mmio_lower_addr,
            access_level=Segment.KERNEL
        )
        self._register_memory_segment(self._mmio_segment)

        # Kernel Data
        self._kdata_segment = MIPSMemorySegment(
            'Kernel Data',
            upper_address=self.config.kdata_upper_addr,
            lower_address=self.config.kdata_lower_addr,
            access_level=Segment.KERNEL
        )
        self._register_memory_segment(self._kdata_segment)

        # Kernel Text
        self._ktext_segment = MIPSTextMemorySegment(
            'Kernel Text',
            upper_address=self.config.ktext_upper_addr,
            lower_address=self.config.ktext_lower_addr,
            access_level=Segment.KERNEL
        )
        self._register_memory_segment(self._ktext_segment)

        # Stack (Grows downward)
        self._stack_segment = MIPSMemorySegment(
            'Stack',
            upper_address=self.config.stack_upper_addr,
            lower_address=self.config.stack_lower_addr,
            access_level=Segment.ALL,
            static=False,
            grow_upwards=False
        )
        self._register_memory_segment(self._stack_segment)

        # Heap (Grows upward)
        self._heap_segment = MIPSMemorySegment(
            'Heap',
            upper_address=self.config.heap_upper_addr,
            lower_address=self.config.heap_lower_addr,
            access_level=Segment.ALL,
            static=False
        )
        self._register_memory_segment(self._heap_segment)

        # User Data
        self._data_segment = MIPSMemorySegment(
            'User Data',
            upper_address=self.config.data_upper_addr,
            lower_address=self.config.data_lower_addr,
            access_level=Segment.ALL
        )
        self._register_memory_segment(self._data_segment)

        # User Text
        self._text_segment = MIPSTextMemorySegment(
            'User Text',
            upper_address=self.config.text_upper_addr,
            lower_address=self.config.text_lower_addr,
            access_level=Segment.ALL
        )
        self._register_memory_segment(self._text_segment)

        # Reserved - Not Implemented
        self._bottom_reserved = MIPSMemorySegment(
            'Reserved',
            upper_address=self.config.lower_reserved_upper_addr,
            lower_address=self.config.lower_reserved_lower_addr,
            access_level=Segment.KERNEL)
        self._register_memory_segment(self._bottom_reserved)
