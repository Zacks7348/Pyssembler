from enum import Enum, auto
import re
import string
from typing import Any, List, Iterable

from pyssembler.mips.hardware import integer


__REGEX__ = r'\n|#.+|".*"|\'.+\'|\$*\.?\w+|:|[^\S\r\n]|\S'
__PATTERN__ = re.compile(__REGEX__)

VALID_SYMBOL_CHARS = string.ascii_letters + string.digits + '_.$'
__SPECIAL_CHARS__ = {'"': '\"', '\\': '\\', 'n': '\n',
                     'r': '\r', 't': '\t', 'b': '\b',
                     '0': '\0'}
__COMMENT_CHAR__ = '#'

__KEYWORDS__ = {}


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
    def __init__(self, raw_text: str, value: Any, type_: TokenType,
                 line: int = 0, line_char: int = 0, char: int = 0, filename: str = None):
        self.raw_text = raw_text
        self.value = value
        self.type = type_
        self.line = line
        self.line_char = line_char
        self.char = char
        self.filename = filename

    def length(self):
        return len(self.raw_text)

    def raw_length(self):
        return len(bytearray(self.raw_text, 'utf-8'))

    def __str__(self):
        return f'Token(text={self.raw_text}, type={self.type})'

    def __repr__(self):
        return f'Token(text={repr(self.raw_text)}, type={self.type}, line={self.line}, char={self.line_char})'


def register_keyword(keyword: str, token_type: TokenType):
    """
    Register a keyword as a specific token type
    :param keyword: The keyword to associate
    :param token_type: The TokenType of the keyword
    """
    if token_type not in __KEYWORDS__:
        __KEYWORDS__[token_type] = set()
    __KEYWORDS__[token_type].add(keyword)


def register_keywords(keywords: Iterable[str], token_type: TokenType):
    """
    Register a list of keywords as a token type
    :param keywords: The list of keywords to associate
    :param token_type: The TokenType of the keywords
    """
    for keyword in keywords:
        register_keyword(keyword, token_type)


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


def _search_keywords(candidate: str) -> TokenType:
    for token_type, keywords in __KEYWORDS__.items():
        if candidate in keywords:
            return token_type
    return None


def _process_candidate(candidate: str, **kwargs) -> Token:
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
    elif (keyword_type := _search_keywords(candidate)) is not None:
        token_type = keyword_type
    elif (i := integer.from_string(candidate)) is not None:
        token_type = TokenType.IMMEDIATE
        processed_value = i
    elif _is_valid_symbol(candidate):
        token_type = TokenType.LABEL

    return Token(candidate, processed_value, token_type, **kwargs)


def tokenize_text(text: str, line_offset: int = 0, char_offset: int = 0, filename: str = None) -> List[List[Token]]:
    """
    Tokenize a string into a list of statements.

    :param text: The string to tokenize
    :param line_offset: Starting point of the line counter
    :param char_offset: Starting point of the char counter
    :param filename: The file the text came from
    :return: A list of lines made up of tokens
    """
    token_list = []
    statements = []
    line_cnt = line_offset
    line_char_cnt = 0
    char_cnt = char_offset
    for raw_token in __PATTERN__.findall(text):
        token = _process_candidate(
            raw_token,
            line=line_cnt,
            line_char=line_char_cnt,
            char=char_cnt,
            filename=filename)
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
            token_type = TokenType.REGISTER
        else:
            token_type = TokenType.match(raw_token)
        token_list.append(Token(raw_token, token_type))
    return token_list



