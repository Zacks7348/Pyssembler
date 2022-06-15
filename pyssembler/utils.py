from collections import namedtuple
from pathlib import Path


class Location:
    def __init__(self, path: Path, line: int, char: int):
        self.path: Path = path
        self.line: int = line
        self.char: int = char

    def __str__(self):
        return f'{self.path}:{self.line}:{self.char}'
