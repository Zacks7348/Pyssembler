from enum import Enum, auto
from typing import Any

from pyssembler.utils import Location


class TokenType(Enum):
    REGISTER = auto()
    MNEMONIC = auto()
    IMMEDIATE = auto()
    DIRECTIVE = auto()
    COMMENT = auto()
    LABEL = auto()
    ASCII = auto()
    CHAR = auto()
    LEFT_P = auto()
    RIGHT_P = auto()
    COLON = auto()
    COMMA = auto()
    WHITESPACE = auto()
    NEWLINE = auto()
    UNKNOWN = auto()


class Token:
    def __init__(
            self,
            raw_text: str,
            value: Any,
            type_: TokenType,
            location: Location = None):
        self.raw_text: str = raw_text
        self.value: Any = value
        self.type: TokenType = type_
        self.location: Location = Location() if location is None else location

    def length(self):
        return len(self.raw_text)

    def raw_length(self, encoding: str = 'utf-8'):
        return len(bytearray(self.raw_text, encoding))

    def __str__(self):
        return f'Token(text={self.raw_text}, type={self.type})'

    def __repr__(self):
        return f'Token(text={repr(self.raw_text)}, type={self.type}, ' \
               f'line={self.location.line}, char={self.location.line_char})'
