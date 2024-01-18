from __future__ import annotations
from collections.abc import Iterator
import typing

if typing.TYPE_CHECKING:
    from .program import AssemblyFile
    from pyssembler.architecture.utils import Source

__all__ = ['Token', 'TokenizedStatement']

_T = typing.TypeVar('_T')


class Token(typing.Generic[_T]):
    def __init__(self, type_: typing.Any, raw_value: str, value: typing.Any, src: Source):
        self.type: _T = type_
        self.raw_value: str = raw_value
        self.value: typing.Any = value
        self.src: Source = src

    @property
    def src_file(self) -> AssemblyFile:
        return self.src.asm_file

    @property
    def src_line(self) -> int:
        return self.src.line_num

    def length(self):
        return len(self.raw_value)

    def bytes_length(self, encoding: str = 'utf-8'):
        return len(bytearray(self.raw_value, encoding))

    def __str__(self):
        return f'Token(raw={self.raw_value},value={self.value},type={self.type})'


_S = typing.TypeVar('_S', bound=Token)


class TokenizedStatement(typing.Generic[_S]):
    def __init__(self, tokens: typing.List[_S] = None):
        self.tokens: typing.List[_S] = tokens or []

    def __iter__(self) -> Iterator[_S]:
        yield from self.tokens

    def __len__(self):
        return len(self.tokens)
