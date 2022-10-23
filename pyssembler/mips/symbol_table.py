from pyssembler.utils import Location


class SymbolTable:
    """
    Represents a MIPS symbol table
    """
    def __init__(self):
        self._table = {}

    def has(self, symbol: str) -> bool:
        """
        Check if a symbol exists in this table

        :param symbol: The symbol to check
        :return: True if the symbol exists
        """
        return symbol in self._table

    def update(self, symbol: str, location: Location = None, address: int = None) -> None:
        """
        Add a symbol to this table.
        Overwrites the symbol if it already exists in this table

        :param symbol: The symbol to update
        :param location: The location of the symbol
        :param address: The address this symbol refers to
        :return: None
        """
        if symbol in self._table:
            if location:
                self._table[symbol]['loc'] = location
            if address:
                self._table[symbol]['addr'] = address
            return
        self._table[symbol] = {'loc': Location, 'addr': address}

    def delete(self, symbol: str) -> None:
        """
        If the symbol exists in this table, delete it

        :param symbol: The symbol to delete
        :return: None
        """
        if symbol in self._table:
            del self._table[symbol]

    def get_adress(self, symbol: str) -> int:
        """
        Return the address of the symbol

        :param symbol: The symbol to get the address of
        :return: int
        """
        if symbol not in self._table:
            raise ValueError(f'Symbol {symbol} does not exist!')
        return self._table[symbol]['addr']

    def get_location(self, symbol: str) -> Location:
        """
        Return the location of the symbol

        :param symbol: The symbol to get the location of
        :return: Location
        """
        if symbol not in self._table:
            raise ValueError(f'Symbol {symbol} does not exist!')
        return self._table[symbol]['loc']

    def clear(self) -> None:
        """
        Clear this table of all symbols

        :return: None
        """
        self._table.clear()

    @property
    def size(self):
        return len(self._table)

    def __str__(self):
        res = f'SymbolTable:\n'
        for key, val in self._table.items():
            res += f'\t{key}: location={val["loc"]}, address={val["addr"]}\n'
        return res

    def __contains__(self, item):
        return item in self._table
