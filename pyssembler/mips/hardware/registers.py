import ctypes
from typing import Union


class MIPSRegister:
    def __init__(
            self,
            address: int,
            name: str,
            read_only: bool = False
    ):
        self.address: int = address
        self.name: str = name
        self._read_only: bool = read_only
        self._value: int = 0

    def read(self, signed=False) -> int:
        if not signed:
            return self._value
        return ctypes.c_int32(self._value).value

    def write(self, val: Union[int, float]) -> None:
        if self._read_only:
            return
        if isinstance(val, int):
            self._value = ctypes.c_uint32(val).value
        elif isinstance(val, float):
            self._value = ctypes.c_uint32.from_buffer(ctypes.c_float(val)).value
        raise ValueError(f'Could not write {val} to register: Expected an int or float')

