from pathlib import Path
from typing import NamedTuple


class Source(NamedTuple):
    asm_file: 'AssemblyFile'
    line_num: int
    line_char: int
    char_num: int

    def __str__(self):
        return f'{self.asm_file}({self.line_num}:{self.line_char})'


class AssemblyFile:
    def __init__(self, path: Path):
        path = Path(path).resolve()
        if not path.exists():
            raise ValueError(f'Assembly file {path} does not exist')
        self.path = Path(path).resolve()
        self._text: str = None
        self._last_modified: int = -1

    @property
    def name(self):
        return self.path.name

    def text(self, cache=True):
        last_modified = self.path.stat().st_mtime

        if last_modified > self._last_modified or not cache:
            # Read file from disk
            self._text = self.read()
            self._last_modified = last_modified

        return self._text

    def read(self):
        with self.path.open('r') as f:
            return f.read()

    def __hash__(self):
        return hash(self.path)

    def __str__(self):
        return str(self.path)
