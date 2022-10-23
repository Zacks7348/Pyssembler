from collections import namedtuple
from typing import Dict

from pyssembler.mips.tokens import TokenType
from pyssembler.mips.mips import Segment


__all__ = [
    'ALIGN_DIRECTIVE',
    'ASCII_DIRECTIVE',
    'ASCIIZ_DIRECTIVE',
    'BYTE_DIRECTIVE',
    'DATA_DIRECTIVE',
    'EXTERN_DIRECTIVE',
    'GLOBL_DIRECTIVE',
    'HALF_DIRECTIVE',
    'INCLUDE_DIRECTIVE',
    'KDATA_DIRECTIVE',
    'KTEXT_DIRECTIVE',
    'SPACE_DIRECTIVE',
    'TEXT_DIRECTIVE',
    'WORD_DIRECTIVE',
    'DIRECTIVES',
]


Directive = namedtuple('Directive', 'name format description segments fmt_tokens')

ALIGN_DIRECTIVE = Directive(
    '.align',
    '.align immediate',
    'Align the next data item on a byte boundary (0=byte, 1=halfword, 2=word)',
    (Segment.DATA, Segment.KDATA),
    [((TokenType.IMMEDIATE, TokenType.CHAR), (0, 1, 2), 1)]
)
ASCII_DIRECTIVE = Directive(
    '.ascii',
    '.ascii "string"',
    'Store the string in memory without a null terminator',
    (Segment.DATA, Segment.KDATA),
    [((TokenType.ASCII,), None, 1)]
)
ASCIIZ_DIRECTIVE = Directive(
    '.asciiz',
    '.asciiz "string"',
    'Store the string in memory with a null terminator',
    (Segment.DATA, Segment.KDATA),
    [((TokenType.ASCII,), None, 1)]
)
BYTE_DIRECTIVE = Directive(
    '.byte',
    '.byte immediate',
    'Store the listed value(s) as bytes in memory',
    (Segment.DATA, Segment.KDATA),
    [((TokenType.IMMEDIATE, TokenType.CHAR), None, '+')]
)
DATA_DIRECTIVE = Directive(
    '.data',
    '.data',
    'Declare the following statements are stored in Data memory segment',
    (Segment.DATA, Segment.KDATA, Segment.TEXT, Segment.KTEXT),
    []
)
EXTERN_DIRECTIVE = Directive(
    '.extern',
    '.extern label immediate',
    'Declare the label and byte length as a global data field',
    (Segment.DATA, Segment.KDATA, Segment.TEXT, Segment.KTEXT),
    [((TokenType.LABEL,), None, 1), ((TokenType.IMMEDIATE, TokenType.CHAR), None, 1)]
)
GLOBL_DIRECTIVE = Directive(
    '.globl',
    '.globl label',
    'Declare the label(s) as global',
    (Segment.DATA, Segment.KDATA, Segment.TEXT, Segment.KTEXT),
    [((TokenType.LABEL,), None, '+')]
)
HALF_DIRECTIVE = Directive(
    '.half',
    '.half immediate',
    'Store the listed value(s) as halfwords in memory',
    (Segment.DATA, Segment.KDATA),
    [((TokenType.IMMEDIATE, TokenType.CHAR), None, '+')]
)
INCLUDE_DIRECTIVE = Directive(
    '.include',
    '.include filename',
    'Insert the contents of a file starting at location of the directive',
    (Segment.DATA, Segment.KDATA, Segment.TEXT, Segment.KTEXT),
    [((TokenType.ASCII,), None, 1)]
)
KDATA_DIRECTIVE = Directive(
    '.kdata',
    '.kdata',
    'Declare the following statements are stored in Kernel Data memory segment',
    (Segment.DATA, Segment.KDATA, Segment.TEXT, Segment.KTEXT),
    []
)
KTEXT_DIRECTIVE = Directive(
    '.ktext',
    '.ktext',
    'Declare the following statements are stored in Kernel Text memory segment',
    (Segment.DATA, Segment.KDATA, Segment.TEXT, Segment.KTEXT),
    []
)
SPACE_DIRECTIVE = Directive(
    '.space',
    '.space immediate',
    'Declare the byte length as a local data field',
    (Segment.DATA, Segment.KDATA, Segment.TEXT, Segment.KTEXT),
    [((TokenType.IMMEDIATE,), None, 1)]
)
TEXT_DIRECTIVE = Directive(
    '.text',
    '.text',
    'Declare the following statements are stored in Text memory segment',
    (Segment.DATA, Segment.KDATA, Segment.TEXT, Segment.KTEXT),
    []
)
WORD_DIRECTIVE = Directive(
    '.word',
    '.word immediate',
    'Store the listed value(s) as words in memory',
    (Segment.DATA, Segment.KDATA),
    [((TokenType.IMMEDIATE, TokenType.CHAR), None, '+')]
)


DIRECTIVES: Dict[str, Directive] = {
    ALIGN_DIRECTIVE.name: ALIGN_DIRECTIVE,
    ASCII_DIRECTIVE.name: ASCII_DIRECTIVE,
    ASCIIZ_DIRECTIVE.name: ASCIIZ_DIRECTIVE,
    BYTE_DIRECTIVE.name: BYTE_DIRECTIVE,
    DATA_DIRECTIVE.name: DATA_DIRECTIVE,
    EXTERN_DIRECTIVE.name: EXTERN_DIRECTIVE,
    GLOBL_DIRECTIVE.name: GLOBL_DIRECTIVE,
    HALF_DIRECTIVE.name: HALF_DIRECTIVE,
    INCLUDE_DIRECTIVE.name: INCLUDE_DIRECTIVE,
    KDATA_DIRECTIVE.name: KDATA_DIRECTIVE,
    KTEXT_DIRECTIVE.name: KTEXT_DIRECTIVE,
    SPACE_DIRECTIVE.name: SPACE_DIRECTIVE,
    TEXT_DIRECTIVE.name: TEXT_DIRECTIVE,
    WORD_DIRECTIVE.name: WORD_DIRECTIVE
}

