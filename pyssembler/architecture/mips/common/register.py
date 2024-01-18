import typing

from pyssembler.architecture.utils import numeric


class MIPSRegister:
    """Base class for MIPS Registers"""
    def __init__(self,
                 address: int,
                 size: int,
                 read_only: bool,
                 names: typing.List[str]):
        self._address: int = address
        self._size: int = size
        self._names: typing.List[str] = names or []
        self._read_only: bool = read_only
        self._value: int = 0

    def read_integer(self, signed=False) -> int:
        if not signed:
            return self._value
        return numeric.to_int(self._value, size=self._size)

    def read_float(self) -> float:
        return numeric.to_float(self._value)

    def read_double(self) -> float:
        return numeric.to_double(self._value)

    def write_integer(self, value: int) -> None:
        self._value = numeric.to_uint(value, size=self._size)

    def write_float(self, value: float) -> None:
        self._value = numeric.from_float(value, size=self._size)

    def write_double(self, value: float) -> None:
        self._value = numeric.from_double(value, size=self._size)
