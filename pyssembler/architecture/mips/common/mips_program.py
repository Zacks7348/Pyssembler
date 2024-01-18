import typing

from .symbol_table import MIPSSymbolTable
from pyssembler.architecture.core import AssemblyFile, PyssemblerProgram


class MIPSProgram(PyssemblerProgram):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Symbol Tables
        self._global_symbols: MIPSSymbolTable = MIPSSymbolTable()
        self._file_symbols: typing.Dict[AssemblyFile, MIPSSymbolTable] = {
            asm_file: MIPSSymbolTable() for asm_file in self
        }

    @property
    def global_symbols(self) -> MIPSSymbolTable:
        return self._global_symbols

    def get_file_symbols(self, asm_file: AssemblyFile) -> MIPSSymbolTable:
        return self._file_symbols[asm_file]