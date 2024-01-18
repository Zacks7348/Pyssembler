import typing

from pyssembler.utils import LoggableMixin
from pyssembler.architecture.utils import numeric


class MIPSRegister(LoggableMixin):
    def __init__(
            self,
            address: int,
            name: str,
            size: int,
            read_only: bool = False,
            default: int = 0
    ) -> None:
        self._log = self.get_logger(suffix=name)
        self._address: int = address
        self._name: str = name
        self._aliases: typing.List[str] = []
        self._size: int = size
        self._read_only: bool = read_only
        self._value: int = 0

    @property
    def address(self) -> int:
        return self._address

    @property
    def names(self) -> typing.List[str]:
        return [self._name] + self._aliases

    def add_alias(self, alias: str) -> None:
        if alias == self._name or alias in self._aliases:
            return
        self._aliases.append(alias)

    def read_integer(self, signed: bool = False) -> int:
        if not signed:
            return self._value

        return numeric.to_int(self._value, size=self._size)

    def read_float(self) -> float:
        return numeric.to_float(self._value)

    def read_double(self) -> float:
        return numeric.to_double(self._value)

    def write_integer(self, value: int) -> None:
        self._log.debug(f'Writing integer: {value}')
        self._value = numeric.to_uint(value, size=self._size)

    def write_float(self, value: float) -> None:
        self._log.debug(f'Writing float: {value}')
        self._value = numeric.from_float(value)

    def write_double(self, value: float) -> None:
        self._log.debug(f'Writing double: {value}')
        self._value = numeric.from_double(value)


class MIPSRegisterFile(LoggableMixin):
    def __init__(self, name: str):
        self._log = self.get_logger(suffix=name)
        self._name: str = name
        self._registers: typing.Dict[int, MIPSRegister] = {}

    @property
    def register_names(self) -> typing.List[str]:
        names = []
        for register in self:
            names += register.names

        return names

    def _init_registers(self) -> None:
        ...

    def add_register(self, register: MIPSRegister) -> None:
        if register.address in self._registers:
            raise ValueError(f'Register already added with address "{register.address}"')

        self._registers[register.address] = register

    def read_integer(self, addr: int = None, name: str = None, **kwargs) -> int:
        return self.get_register(addr=addr, name=name).read_integer(**kwargs)

    def read_float(self, addr: int = None, name: str = None) -> float:
        return self.get_register(addr=addr, name=name).read_float()

    def read_double(self, addr: int = None, name: str = None) -> float:
        return self.get_register(addr=addr, name=name).read_double()

    def write_integer(self, val: int, addr: int = None, name: str = None):
        self.get_register(addr=addr, name=name).write_integer(val)

    def write_float(self, val: float, addr: int = None, name: str = None):
        self.get_register(addr=addr, name=name).write_float(val)

    def write_double(self, val: float, addr: int = None, name: str = None):
        self.get_register(addr=addr, name=name).write_double(val)

    def get_register(self, addr: int = None, name: str = None) -> MIPSRegister:
        if addr is None and name is None:
            raise ValueError(f'Expected a register address or name!')

        if addr is not None and name is not None:
            self._log.warning(f'Received both address ({addr}) and name ("{name}"): Defaulting to address')

        if addr is not None:
            if addr not in self._registers:
                raise ValueError(f'Invalid register address: {addr}')
            return self._registers[addr]

        if name is not None:
            for register in self:
                if name in register.names:
                    return register
            raise ValueError(f'Invalid register name: {name}')

    def __iter__(self) -> typing.Iterable[MIPSRegister]:
        yield from self._registers.values()
