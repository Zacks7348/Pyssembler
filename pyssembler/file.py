from pathlib import Path

from pyssembler.mips import SymbolTable


class ASMFile:
    """
    Represents an assembly text file
    """
    def __init__(self, path: Path):
        self._path = path
        self.symbols = SymbolTable()

    @property
    def path(self):
        return self._path
