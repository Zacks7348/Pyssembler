from enum import Enum, IntFlag, auto


__all__ = ['MIPSTokenType', 'Segment']


class MIPSTokenType(IntFlag):
    UNKNOWN = auto()
    NEWLINE = auto()
    WHITESPACE = auto()
    COMMA = auto()
    COLON = auto()
    LEFT_PARENTHESIS = auto()
    RIGHT_PARENTHESIS = auto()
    REGISTER = auto()
    MNEMONIC = auto()
    DIRECTIVE = auto()
    IMMEDIATE = auto()
    ASCII = auto()
    CHAR = auto()
    COMMENT = auto()
    LABEL = auto()

    IMMEDIATE_LIKE = IMMEDIATE | CHAR | LABEL
    IMMEDIATE_LIKE_VALUE = IMMEDIATE | CHAR
    INSTR_FIELD = REGISTER | IMMEDIATE_LIKE_VALUE

    def __str__(self):
        return self.name.replace('_', ' ').capitalize()


class Segment(IntFlag):
    DATA = auto()
    KDATA = auto()
    TEXT = auto()
    KTEXT = auto()

    # Useful flags
    ANY_DATA = DATA | KDATA
    ANY_TEXT = TEXT | KTEXT
    KERNEL = KDATA | KDATA
    USER = DATA | TEXT
    ALL = KERNEL | USER
    NONE = 0
