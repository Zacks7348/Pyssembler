from __future__ import annotations
import typing

from .mips_enums import *
from .mips_token import MIPSToken
from .mips_program import MIPSProgram
from pyssembler.architecture.core import TokenizedStatement

if typing.TYPE_CHECKING:
    from .directives import MIPSDirective
    from .instruction import MIPSBasicInstruction


class MIPSTokenizedStatement(TokenizedStatement[MIPSToken]):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __str__(self):
        return ' '.join([t.raw_value for t in self.tokens])


class MIPSStatement(MIPSTokenizedStatement):
    def __init__(
            self,
            program: MIPSProgram,
            tokens: typing.List[MIPSToken] = None,
            label: MIPSToken = None,
            segment: Segment = Segment.TEXT
    ) -> None:
        super().__init__(tokens)
        self._program: MIPSProgram = program
        self.label: MIPSToken = label
        self.segment: Segment = segment
        self.address: int = None
        self.directive_impl: MIPSDirective = None
        self.instr_impl: MIPSBasicInstruction = None

    @property
    def program(self) -> MIPSProgram:
        return self._program

    @property
    def identifier(self) -> MIPSToken:
        return self.tokens[0]

    @property
    def src(self):
        return self.identifier.src

    def is_directive(self) -> bool:
        return self.identifier.type == MIPSTokenType.DIRECTIVE

    def is_instruction(self) -> bool:
        return self.identifier.type == MIPSTokenType.MNEMONIC

    def execute(self):
        if self.is_instruction():
            self.instr_impl.execute(self)
