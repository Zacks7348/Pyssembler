"""This module contains core logic for simulating the
MIPS Architecture Release 6 Memory Model.
"""
from __future__ import annotations
from abc import abstractmethod
import typing

from .constants import MIPSMemorySize
from ..mips_exceptions import *
from ..mips_enums import Segment
from pyssembler.architecture.utils import numeric

if typing.TYPE_CHECKING:
    from ..statement import MIPSStatement


class MIPSMemorySegment:
    """Represents a segment of MIPS memory"""

    def __init__(
            self,
            name: str,
            lower_address: int = 0,
            upper_address: int = 0,
            access_level: Segment = Segment.ALL,
            static: bool = True,
            grow_upwards: bool = True,
    ):
        self.name: str = name
        self._lower_address: int = lower_address  # Inclusive
        self._upper_address: int = upper_address  # Inclusive
        self._access_level: Segment = access_level
        self._static: bool = static
        self._grow_upwards: bool = grow_upwards
        self._memory: typing.Dict[int, int] = {}

        self.validate_address_range()

    @property
    def lower_address(self) -> int:
        return self._lower_address

    @property
    def upper_address(self) -> int:
        return self._upper_address

    @property
    def access_level(self) -> Segment:
        return self._access_level

    def grow(self, num_bytes: int) -> None:
        ...

    def update_range(self, lower: int = None, upper: int = None):
        """Update the memory addressing range of this segment"""
        original_lower = self._lower_address
        original_upper = self._upper_address

        if lower is not None:
            self._lower_address = lower

        if upper is not None:
            self._upper_address = upper

        # Verify that the current range is valid
        self.validate_address_range()

    def address_in_segment(self, addr: int) -> bool:
        return self._lower_address <= addr <= self._upper_address

    def validate_address_range(self):
        if not (self._lower_address <= self._upper_address):
            raise RuntimeError(f'Invalid address range')

    def read_byte(self, addr: int, signed: bool = False) -> int:
        """Read a byte from memory starting at addr.

        :param addr: Address to start reading from.
        :param signed: Optional, read value as signed integer if True
                       (default=False).
        """
        self._validate_address(addr)
        val = self._memory.get(addr, 0)
        if signed:
            return numeric.to_int(val, MIPSMemorySize.BYTE)

        # Assume values are saved as unsigned bytes
        return val

    def write_byte(self, addr: int, val: int) -> None:
        """Write a byte of data into memory.

        Values are saved as unsigned bytes.

        :param addr: The address to write to.
        :param val: The value to write.
        """
        self._validate_address(addr)
        val = numeric.to_uint(val, MIPSMemorySize.BYTE)
        self._memory[addr] = val

    def _validate_address(self, addr: int):
        if not self.address_in_segment(addr):
            # TODO: Raise address error
            return


class MIPSTextMemorySegment(MIPSMemorySegment):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._instr_memory: typing.Dict[int, MIPSStatement] = {}

    def read_instruction(self, addr: int) -> MIPSStatement:
        self._validate_address(addr)
        return self._instr_memory.get(addr, None)

    def write_instruction(self, addr: int, statement: MIPSStatement) -> None:
        self._validate_address(addr)
        self._instr_memory[addr] = statement


class MIPSMemory:
    """Base class for MIPS memory applications"""

    def __init__(self):
        self._memory_segments: typing.List[MIPSMemorySegment] = []
        self._init_segments()

    @abstractmethod
    def _init_segments(self) -> None:
        ...

    def read_byte(
            self,
            start_addr: int,
            signed: bool = False,
            program_segment: Segment = Segment.ALL
    ) -> int:
        """Read a single byte from memory."""
        return self.read_bytes(
            start_addr,
            MIPSMemorySize.BYTE // MIPSMemorySize.BYTE,
            signed=signed,
            program_segment=program_segment
        )

    def read_halfword(
            self,
            start_addr: int,
            signed: bool = False,
            downward: bool = False,
            program_segment: Segment = Segment.ALL
    ) -> int:
        """Read a half-word from memory."""
        return self.read_bytes(
            start_addr,
            MIPSMemorySize.HWORD // MIPSMemorySize.BYTE,
            signed=signed,
            downward=downward,
            program_segment=program_segment
        )

    def read_word(
            self,
            start_addr: int,
            signed: bool = False,
            downward: bool = False,
            program_segment: Segment = Segment.ALL
    ) -> int:
        """Read a word from memory."""
        return self.read_bytes(
            start_addr,
            MIPSMemorySize.WORD // MIPSMemorySize.BYTE,
            signed=signed,
            downward=downward,
            program_segment=program_segment
        )

    def read_doubleword(
            self,
            start_addr: int,
            signed: bool = False,
            downward: bool = False,
            program_segment: Segment = Segment.ALL
    ) -> int:
        """Read a double-word from memory."""
        return self.read_bytes(
            start_addr,
            MIPSMemorySize.DWORD // MIPSMemorySize.BYTE,
            signed=signed,
            downward=downward,
            program_segment=program_segment
        )

    def read_instruction(self, addr: int, program_segment: Segment = Segment.ALL) -> MIPSStatement:
        mem_segment = self._get_memory_segment(
            addr,
            reason=MIPSExceptionCodes.ADDRL,
            program_segment=program_segment
        )

        if not isinstance(mem_segment, MIPSTextMemorySegment):
            return None

        return mem_segment.read_instruction(addr)

    def read_bytes(
            self,
            start_addr: int,
            num_bytes: int,
            signed: bool = False,
            downward: bool = False,
            program_segment: Segment = Segment.ALL
    ) -> int:
        """Read a series of bytes from memory.

        By default, all of simulated is accessible. Operating modes can be
        simulated by using the `segment` keyword argument.

        :param start_addr: The address to start reading from.
        :param num_bytes: The number of bytes to read.
        :param signed: Optional, read as a signed integer if True (default = False).
        :param downward: Optional, read down memory instead of upwards (default = False).
        :param program_segment: Optional, segment of program where memory access is occurring
                                (default = ALL).
        """
        read_bytes = []
        for i in range(num_bytes):
            addr = start_addr + i if not downward else start_addr - i
            mem_segment = self._get_memory_segment(addr, MIPSExceptionCodes.ADDRL, program_segment=program_segment)
            read_bytes.append(mem_segment.read_byte(addr))

        return numeric.from_bytes(read_bytes, signed=signed)

    def write_byte(
            self,
            start_addr: int,
            val: int,
            program_segment: Segment = Segment.ALL
    ) -> None:
        """Write a single byte into memory."""
        self.write_bytes(
            start_addr,
            val,
            MIPSMemorySize.BYTE // MIPSMemorySize.BYTE,
            program_segment=program_segment
        )

    def write_halfword(
            self,
            start_addr: int,
            val: int,
            downward: bool = False,
            program_segment: Segment = Segment.ALL
    ) -> None:
        """Write a half-word into memory."""
        self.write_bytes(
            start_addr,
            val,
            MIPSMemorySize.HWORD // MIPSMemorySize.BYTE,
            downward=downward,
            program_segment=program_segment
        )

    def write_word(
            self,
            start_addr: int,
            val: int,
            downward: bool = False,
            program_segment: Segment = Segment.ALL
    ) -> None:
        """Write a word into memory."""
        self.write_bytes(
            start_addr,
            val,
            MIPSMemorySize.WORD // MIPSMemorySize.BYTE,
            downward=downward,
            program_segment=program_segment
        )

    def write_doubleword(
            self,
            start_addr: int,
            val: int,
            downward: bool = False,
            program_segment: Segment = Segment.ALL
    ) -> None:
        """Write a double-word into memory."""
        self.write_bytes(
            start_addr,
            val,
            MIPSMemorySize.DWORD // MIPSMemorySize.BYTE,
            downward=downward,
            program_segment=program_segment
        )

    def write_instruction(
            self,
            addr: int,
            statement: MIPSStatement,
            program_segment: Segment = Segment.ALL
    ) -> None:
        mem_segment = self._get_memory_segment(
            addr,
            reason=MIPSExceptionCodes.ADDRS,
            program_segment=program_segment
        )

        if not isinstance(mem_segment, MIPSTextMemorySegment):
            return None

        mem_segment.write_instruction(addr, statement)

    def write_bytes(
            self,
            start_addr: int,
            val: int,
            num_bytes: int,
            downward: bool = False,
            program_segment: Segment = Segment.ALL
    ) -> None:
        """Write a series of bytes into memory.

        :param start_addr: The address to writing to.
        :param val: The integer value to write.
        :param num_bytes: The number of bytes to write.
        :param downward: Optional, write down memory instead of upwards (default = False).
        :param program_segment: Optional, segment of program where memory access is occurring
                                (default = ALL).
        """
        val = numeric.to_uint(val, num_bytes * MIPSMemorySize.BYTE)
        val_bytes = numeric.to_bytes(val, num_bytes)

        for i, byte in enumerate(val_bytes):
            addr = start_addr + i if not downward else start_addr - i
            mem_segment = self._get_memory_segment(addr, MIPSExceptionCodes.ADDRS, program_segment=program_segment)
            mem_segment.write_byte(addr, byte)

    def _get_memory_segment(
            self,
            addr: int,
            reason: int,
            program_segment: Segment = Segment.ALL
    ) -> MIPSMemorySegment:
        """Helper function to return the memory segment associated with an address."""
        for mem_segment in self._memory_segments:
            if mem_segment.address_in_segment(addr):
                if mem_segment.access_level not in program_segment:
                    raise AddressErrorException(addr, reason)
                return mem_segment

        raise ValueError(f'Address Error!')

    def _register_memory_segment(self, segment: MIPSMemorySegment) -> None:
        # Raises ValueError if fails check
        self._validate_segment(segment)

        # Add to segments list
        self._memory_segments.append(segment)

    def _validate_segment(self, segment: MIPSMemorySegment) -> None:
        if not self._memory_segments:
            return

        valid = False
        for other in self._memory_segments:
            if other is segment:
                continue

            # Check if segments overlap
            if segment.lower_address <= other.upper_address and segment.upper_address >= other.lower_address:
                raise ValueError(f'Memory segments cannot overlap!')

            # Check if segments are adjacent
            if abs(segment.lower_address - other.upper_address) == 1 or abs(
                    segment.upper_address - other.lower_address) == 1:
                valid = True

        if not valid:
            raise ValueError(f'Segment must be adjacent to another segment!')
