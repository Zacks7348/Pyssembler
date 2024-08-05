from __future__ import annotations
from pathlib import Path
import typing

__all__ = [
    'PyssemblerProgram',
    'Source',
    'SourceLine',
    'AssemblyFile'
]


class PyssemblerProgram:
    """Represents an executable assembly program"""

    def __init__(self, src_files: typing.List['AssemblyFile']):
        self.src_files: typing.List[AssemblyFile] = src_files

    @property
    def main_file(self):
        if not self.src_files:
            return None

        return self.src_files[0]

    def __iter__(self):
        yield from self.src_files

    def __len__(self):
        return len(self.src_files)


class Source(typing.NamedTuple):
    """Represents text from a source file"""
    asm_file: 'AssemblyFile'
    line_num: int
    line_char: int
    char_num: int

    def __str__(self):
        return f'{self.asm_file}({self.line_num}:{self.line_char})'


class SourceLine(typing.NamedTuple):
    """Represents a line of assembly from a source file"""
    src_text: str
    src_line: int
    src_file: 'AssemblyFile'


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

    def get_source_line(self, lineno: int):
        if lineno < 0:
            return None

        lines = self.text().splitlines()
        if lineno >= len(lines):
            return None

        return SourceLine(lines[lineno] + '\n', lineno, self)

    def read(self):
        with self.path.open('r') as f:
            return f.read()

    def __hash__(self):
        return hash(self.path)

    def __eq__(self, other: 'AssemblyFile'):
        if isinstance(other, AssemblyFile):
            return self.path == other.path

        return super().__eq__(other)

    def __str__(self):
        return self.name
