from __future__ import annotations
import logging
import re
import string
from typing import List, Iterable, Union, TYPE_CHECKING

from pyssembler.mips.directives import DIRECTIVES, INCLUDE_DIRECTIVE
from pyssembler.mips.hardware import integer, REGISTERS
from pyssembler.mips.instructions import instruction_set as instr_set
from pyssembler.mips.tokens import Token, TokenType
from pyssembler.utils import Location


if TYPE_CHECKING:
    from pathlib import Path


__LOGGER__ = logging.getLogger(__name__)

__REGEX__ = r'\n|#.+|".*"|\'.+\'|\$*\.?\w+|:|[^\S\r\n]|\S'
__PATTERN__ = re.compile(__REGEX__)

VALID_SYMBOL_CHARS = string.ascii_letters + string.digits + '_.$'
__SPECIAL_CHARS__ = {'"': '\"', '\\': '\\', 'n': '\n',
                     'r': '\r', 't': '\t', 'b': '\b',
                     '0': '\0'}
__COMMENT_CHAR__ = '#'

__KEYWORDS__ = {}


def _is_valid_symbol(raw_token: str) -> bool:
    """
    Returns True if the raw_token is a valid symbol

    :param raw_token: The string to test
    :return: True
    """
    if not raw_token:
        return False
    if not raw_token[0].isalpha():
        # First character has to be a letter
        return False

    for c in raw_token[1:]:
        if c not in VALID_SYMBOL_CHARS:
            return False
    return True


def _process_candidate(candidate: str, location: Location) -> Token:
    symbols = {
        '(': TokenType.LEFT_P,
        ')': TokenType.RIGHT_P,
        ':': TokenType.COLON,
        ',': TokenType.COMMA,
        '\n': TokenType.NEWLINE
    }
    processed_value = candidate
    token_type = TokenType.UNKNOWN

    if candidate in symbols:
        token_type = symbols[candidate]
    elif candidate.isspace():
        # Newline chars will already be captured in symbols check
        token_type = TokenType.WHITESPACE
    elif candidate.startswith('"') and candidate.endswith('"') and len(candidate) > 1:
        token_type = TokenType.ASCII
    if candidate.startswith("'") and candidate.endswith("'") and len(candidate) in {3, 4}:
        if len(candidate) == 4:
            if candidate.startswith('\\') and candidate[2] in __SPECIAL_CHARS__:
                token_type = TokenType.CHAR
                processed_value = integer.from_string(f"'{__SPECIAL_CHARS__[candidate[2]]}'")
        else:
            token_type = TokenType.CHAR
            processed_value = integer.from_string(candidate)
    elif candidate.startswith(__COMMENT_CHAR__):
        token_type = TokenType.COMMENT
    elif candidate in DIRECTIVES:
        token_type = TokenType.DIRECTIVE
    elif candidate in instr_set.BASIC_INSTRUCTIONS:
        token_type = TokenType.MNEMONIC
    elif candidate in REGISTERS:
        token_type = TokenType.REGISTER
    elif (i := integer.from_string(candidate)) is not None:
        token_type = TokenType.IMMEDIATE
        processed_value = i
    elif _is_valid_symbol(candidate):
        token_type = TokenType.LABEL

    return Token(candidate, processed_value, token_type, location)


def tokenize_text(text: str, line_offset: int = 0, char_offset: int = 0,
                  filename: Union[str, Path] = None) -> List[List[Token]]:
    """
    Tokenize a string into a list of statements.

    :param text: The string to tokenize
    :param line_offset: Starting point of the line counter
    :param char_offset: Starting point of the char counter
    :param filename: The file the text came from
    :return: A list of lines made up of tokens
    """
    __LOGGER__.debug(f'Tokenizing text...')
    token_list = []
    statements = []
    line_cnt = line_offset
    line_char_cnt = 0
    char_cnt = char_offset
    for raw_token in __PATTERN__.findall(text):
        loc = Location(filename, line_cnt, line_char_cnt, char_cnt)
        token = _process_candidate(raw_token, loc)
        token_list.append(token)
        if token.type == TokenType.NEWLINE:
            line_cnt += 1
            line_char_cnt = 0
            statements.append(token_list)
            token_list = []
        else:
            line_char_cnt += token.length()
        char_cnt += token.length()
    if token_list:
        statements.append(token_list)
    return statements


def tokenize_instr_format(text: str):
    token_list = []
    for raw_token in __PATTERN__.findall(text):
        if raw_token in ('rd', 'rs', 'rt'):
            token = Token(raw_token, raw_token, TokenType.REGISTER)
        elif raw_token in ('immediate', 'offset', 'sel'):
            token = Token(raw_token, raw_token, TokenType.IMMEDIATE)
        else:
            token = _process_candidate(raw_token, None)

        if token.type != TokenType.WHITESPACE:
            token_list.append(token)
    return token_list



