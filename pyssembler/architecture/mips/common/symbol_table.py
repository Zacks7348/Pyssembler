import typing

from pyssembler.architecture.utils import Source


class MIPSSymbolTable:
    def __init__(self):
        self._table: typing.Dict[str, Symbol] = {}

    def has_symbol(self, name: str):
        return name in self._table

    def add_symbol(self, name: str, source: Source = None, address: int = None):
        symbol = Symbol(name, source=source, address=address)
        self._table[name] = symbol

    def remove_symbol(self, name: str):
        self._table.pop(name, None)

    def get_symbol(self, name: str):
        return self._table[name]

    def clear(self):
        self._table.clear()


class Symbol:
    def __init__(self, name: str, source: Source = None, address: int = None):
        self.name: str = name
        self.source: Source = source
        self.address: int = address
