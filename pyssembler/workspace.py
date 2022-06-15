from pathlib import Path
from typing import Dict


from pyssembler.mips.symbol_table import SymbolTable


class Workspace:
    """
    Represents a Pyssembler Workspace. Similar to a workspace in Visual Studio Code, a
    Pyssembler Workspace is a directory where the root of that directory acts as the
    root of the Workspace. Relative includes in this workspace will be resolved relative
    to the workspace's root.
    """
    def __init__(self, root: Path):
        self._root = root
        self.global_symbol_table: SymbolTable = SymbolTable('Global')
        self.local_symbol_tables: Dict[str, SymbolTable] = {}

        # Directory Cache. Store the last time the directory was accessed.
        # path: {'asm_files': [], 'time': 0}
        self.__dir_cache = {}

    @property
    def root(self):
        return self._root

    def get_symbol_table(self, file: Path = None):
        """
        Returns the symbol table attached to a file or global table if None
        :param file: The file to get the symbol table of.
        :return: SymbolTable
        """
        if not file:
            return self.global_symbol_table

        return self.local_symbol_tables.get(file, None)

    def find_asm_files(self, root: Path):
        asm_files = []
        for child in root.iterdir():
            if child.is_dir():
                # Check cache
                if child in self.__dir_cache:
                    if child.stat().st_mtime < self.__dir_cache[child]['time']:
                        asm_files += self.__dir_cache[child]['files']
                        continue
                # Not in cache or cache out of date
                asm_files += self.find_asm_files(child)
                self.__dir_cache[]

            elif child.is_file():
                if child.suffix == '.asm':
                    asm_files.append(child)
        return asm_files

