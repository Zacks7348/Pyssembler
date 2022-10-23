from __future__ import annotations
from typing import List, TYPE_CHECKING

from pyssembler.mips.tokens import Token, TokenType

if TYPE_CHECKING:
    from pyssembler.mips.mips import Segment


class MIPSStatement:
    def __init__(self, tokens: List[Token], segment: Segment, label: Token = None):
        self.tokens: List[Token] = tokens
        self.segment: Segment = segment
        self.label: Token = label

    def is_instruction(self):
        return self.tokens[0].type == TokenType.MNEMONIC

    def is_directive(self):
        return self.tokens[0].type == TokenType.DIRECTIVE

    def __getitem__(self, key):
        return self.tokens[key]

    def __str__(self):
        if self.label:
            return f'MIPSStatement({self.label.raw_text}: {" ".join([t.raw_text for t in self.tokens])})'
        return f'MIPSStatement({" ".join([t.raw_text for t in self.tokens])})'

