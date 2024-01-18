import typing

from .. import numeric, constants
from pyssembler.utils import LoggableMixin


class MIPSRegister:
    def __init__(
            self,
            address: int,
            name: str,
            size: int = constants.WORD,
            read_only: bool = False
    ):
        self.address: int = address
        self.name: str = name
        self._read_only: bool = read_only
        self._value: int = 0
        self._size: int = size

    def read(self, signed=False) -> int:
        if not signed:
            return self._value
        return numeric.to_int(self._value, size=self._size)

    def write(self, val: int) -> None:
        if self._read_only:
            return
        self._value = numeric.to_uint(val, size=self._size)

    def __str__(self):
        return f'MIPSRegister(addr={self.address}, val={self._value})'


class MIPSRegisterFile(LoggableMixin):
    def __init__(self, name: str, size: int = constants.WORD, real_numbers: bool = False):
        self._log = self._get_logger(suffix=name)
        self.name = name
        self._size = size
        self._real_numbers: bool = real_numbers
        self._registers: typing.Dict[int, MIPSRegister] = {}
        self._name_map: typing.Dict[str, MIPSRegister] = {}

    def add_register(self, addr: int, name: str, **kwargs):
        reg = MIPSRegister(addr, name, size=self._size, **kwargs)
        self._log.debug(f'Adding register: {reg}...')
        if addr in self._registers or name in self._name_map:
            raise ValueError(f'Register already exists with address {addr} and/or name "{name}"')
        self._registers[addr] = reg
        self._name_map[reg.name] = reg

    def read_integer(self, addr: int = None, name: str = None, **kwargs) -> int:
        return self._get_register(addr=addr, name=name).read(**kwargs)

    def read_float(self, addr: int = None, name: str = None) -> float:
        return numeric.to_float(self._get_register(addr=addr, name=name).read())

    def read_double(self, addr: int = None, name: str = None) -> float:
        reg1 = self._get_register(addr=addr, name=name)
        if self._size == constants.DWORD:
            return numeric.to_double(reg1.read())

        # Registers are WORD sized
        reg2 = self._get_register(addr=reg1.address+1)
        return numeric.to_double((reg1.read() << self._size) | reg2.read())

    def write_integer(self, val: int, addr: int = None, name: str = None):
        self._get_register(addr=addr, name=name).write(val)

    def write_float(self, val: float, addr: int = None, name: str = None):
        self._get_register(addr=addr, name=name).write(
            numeric.from_float(val, size=constants.WORD))

    def write_double(self, val: float, addr: int = None, name: str = None):
        reg1 = self._get_register(addr=addr, name=name)
        val = numeric.from_double(val, size=constants.DWORD)
        if self._size == constants.DWORD:
            reg1.write(val)
            return

        reg2 = self._get_register(addr=reg1.address+1)
        reg1.write(numeric.get_bytes(val, 0, 4))
        reg2.write(numeric.get_bytes(val, 4, 8))

    def string_table(self, columns: int = 4) -> str:
        res = ''
        for i, reg in enumerate(self, start=1):
            res += f'[{reg.name}: {reg.read()}]'
            if i % columns == 0 and i != 0:
                res += '\n'
            else:
                res += ', '

        return res

    def register_names(self) -> typing.Generator[str, None, None]:
        yield from self._name_map.keys()

    def _get_register(self, addr: int = None, name: str = None) -> MIPSRegister:
        if addr is None and name is None:
            raise ValueError(f'Expected a register address or name!')
        if addr is not None and name is not None:
            self._log.warning(f'Recieved both address ({addr}) and name ("name"): Reading using address')

        if addr is not None:
            if addr not in self._registers:
                raise ValueError(f'Invalid register address: {addr}')
            return self._registers[addr]

        if name is not None:
            if name not in self._name_map:
                raise ValueError(f'Invalid register name: {name}')
            return self._name_map[name]

    def __iter__(self) -> typing.Generator[MIPSRegister, None, None]:
        yield from self._registers.values()

    def __str__(self):
        return self.string_table()
