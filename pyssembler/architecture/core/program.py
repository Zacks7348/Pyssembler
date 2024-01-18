from __future__ import annotations
from pathlib import Path
import typing

__all__ = ['PyssemblerProgram',
           'SourceLine',
           'AssemblyFile']


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
