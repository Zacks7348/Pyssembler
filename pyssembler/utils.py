import logging
from pathlib import Path


class LoggableMixin:
    def _get_logger(self, name=None):
        if name is None:
            name = self.__class__.__name__
        return logging.getLogger(f'{self.__class__.__module__}.{name}')


class Location:
    def __init__(
            self,
            path: Path = None,
            line: int = None,
            line_char: int = None,
            char: int = None):
        self.path: Path = path
        self.line: int = line
        self.line_char: int = line_char
        self.char: int = char

    def __str__(self):
        return f'{self.path}({self.line},{self.char})'
