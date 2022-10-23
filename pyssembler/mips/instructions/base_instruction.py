from __future__ import annotations
from enum import Enum
from typing import List, TYPE_CHECKING

from pyssembler.mips.tokens import TokenType, Token


if TYPE_CHECKING:
    from pyssembler.mips.statement import MIPSStatement


class InstructionType(Enum):
    R_TYPE = 0
    I_TYPE = 1
    B_TYPE = 2
    J_TYPE = 3
    J_SHIFT_TYPE = 4

    @staticmethod
    def get_type(type_: str) -> 'InstructionType':
        for instr_type in InstructionType:
            if instr_type.name == f'{type_}_TYPE':
                return instr_type


class MIPSInstruction:
    def __init__(self, mnemonic: str, format_: str, description: str):
        self.mnemonic: str = mnemonic
        self.format: str = format_
        self._fmt_tokens: List[Token] = None
        self.description: str = description

    @property
    def fmt_tokens(self):
        # Lazy loading. This gives time for all mnemonics to be registered
        # in the tokenizer
        if self._fmt_tokens is None:
            from pyssembler.mips.tokenizer import tokenize_instr_format
            self._fmt_tokens = tokenize_instr_format(self.format)
        return self._fmt_tokens

    def match(self, statement: MIPSStatement) -> bool:
        """
        Returns True if the sequence of tokens matches the formatting
        of this instruction.

        Assumes all whitespaces, comments, and label+colons have been removed
        :param statement: The statement to test
        :return: bool
        """
        # Easy check
        if len(statement.tokens) < len(self.fmt_tokens):
            return False

        # First token should be this mnemonic
        if statement.tokens[0].type != TokenType.MNEMONIC or statement.tokens[0].raw_text != self.mnemonic:
            return False

        # All tokens should match
        for token, fmt_token in zip(statement.tokens, self.fmt_tokens):
            if fmt_token.type == TokenType.IMMEDIATE:
                # Token can either be an immediate, char, or label
                if token.type not in (TokenType.IMMEDIATE, TokenType.CHAR, TokenType.LABEL):
                    return False
            elif token.type != fmt_token.type:
                return False
        return True


    def __str__(self):
        return f'{self.mnemonic} MIPS Instruction'

    def __repr__(self):
        return f'{self.__class__.__name__}(mnemonic={self.mnemonic}, format={self.format}, description={self.description})'


class MIPSBasicInstruction(MIPSInstruction):
    """
    The base instruction class all MIPS instructions derive from
    """
    def __init__(
            self,
            mnemonic: str,
            format_: str,
            description: str,
            encoding: str,
            type_: InstructionType):
        super().__init__(mnemonic, format_, description)
        self.encoding: str = encoding
        self.type: InstructionType = type_

    @staticmethod
    def mnemonic():
        return None

    def assemble(self, statement):
        pass

    def simulate(self, cpu):
        pass

    def __str__(self):
        return f'{self.mnemonic} MIPS Basic Instruction'


class MIPSPseudoInstruction(MIPSInstruction):
    def __init__(self, mnemonic, format_: str, description: str, expansion: List[MIPSBasicInstruction]):
        super().__init__(mnemonic, format_, description)
        self.expansion = expansion

    def expand(self):
        pass

    def __str__(self):
        return f'{self.mnemonic} MIPS Psuedo Instruction'
