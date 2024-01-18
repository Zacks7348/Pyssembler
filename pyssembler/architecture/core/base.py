"""This module contains Pyssembler interfaces different architectures must
implement to be compatible with the simulation framework.

These classes should not be used directly. Instead, architectures
should implement their own that derive from these ABCs.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from collections.abc import Iterator
import inspect
import typing

from .exceptions import AssemblerException, TokenizationException
from pyssembler.utils import LoggableMixin

if typing.TYPE_CHECKING:
    from .program import PyssemblerProgram
    from .token import Token, TokenizedStatement
    from pyssembler.architecture.utils import AssemblyFile

__all__ = [
    'PyssemblerAssembler',
    'PyssemblerCPU',
    'PyssemblerInstructionSet',
    'PyssemblerBasicInstruction',
    'PyssemblerPseudoInstruction',
]


_T = typing.TypeVar('_T', bound='PyssemblerCPU')


class PyssemblerAssembler(typing.Generic[_T], LoggableMixin):
    def __init__(self, cpu: _T):
        self._cpu: _T = cpu
        self._log = self.get_logger()
        self._log.debug(f'Initializing directives...')
        self.__init_directives()

    @abstractmethod
    def assemble_program(self, program: PyssemblerProgram, **kwargs) -> None:
        ...

    def tokenize_program(self, program: PyssemblerProgram) -> typing.List[TokenizedStatement]:
        """Base implementation for tokenizing a program"""
        statements = []
        for asm_file in program.src_files:
            statements += self.tokenize_file(asm_file)

        return statements

    def tokenize_file(self, file: AssemblyFile, **kwargs) -> typing.List[TokenizedStatement]:
        return self.tokenize_text(file.text(), **kwargs)

    @abstractmethod
    def tokenize_text(self,
                      text: str,
                      line_start: int = 0,
                      char_start: int = 0,
                      asm_file: AssemblyFile = None,
                      ignore_whitespace: bool = True,
                      ignore_comments: bool = True) -> typing.List[TokenizedStatement]:
        ...

    # Asserts
    @staticmethod
    def _assert_token_type(token: Token, *expected_types: str, msg: str = None):
        if token.type in expected_types:
            return

        if msg is not None:
            raise TokenizationException(msg)

        if len(expected_types) == 1:
            raise TokenizationException(f'Expected {expected_types[0]}: Got {token}')

        raise TokenizationException(f'Expected one of ({", ".join(expected_types)}): Got {token}')

    def __init_directives(self):
        ...


# ----------------------------------------------------------------------------
# Simulation
# ----------------------------------------------------------------------------
class PyssemblerCPU(ABC, LoggableMixin):
    """Base class for all CPU simulation models.

    Implementations of this class are meant to simulate a single CPU core.
    """
    def __init__(self):
        self._log = self.get_logger()

    @property
    @abstractmethod
    def instruction_set(self) -> 'PyssemblerInstructionSet':
        ...

    @property
    @abstractmethod
    def assembler(self) -> PyssemblerAssembler:
        ...

    @abstractmethod
    def get_register_names(self) -> typing.List[str]:
        ...

    @abstractmethod
    def load_program_to_memory(self, program: PyssemblerProgram) -> None:
        ...

    @abstractmethod
    def clear_program_memory(self) -> None:
        ...

    @abstractmethod
    def execute(self) -> None:
        ...

    @abstractmethod
    def step_execution(self) -> None:
        ...

    def _stop_execution(self) -> None:
        """Helper function to indicate CPU execution has stopped

        All other execution logic should finish before this is called.
        """
        raise Exception('Stop')  # TODO: Custom exception


# ----------------------------------------------------------------------------
# Instructions
# ----------------------------------------------------------------------------
class PyssemblerBasicInstruction(typing.Generic[_T], LoggableMixin):
    """Base class for all basic instructions.

    A basic instruction is a single assembly statement that is part of an
    architectures instruction set. It can be assembled directly into binary.
    """

    def __init__(self,
                 mnemonic: str,
                 full_name: str,
                 operands: str,
                 description: str,
                 operation: str,
                 encoding: str,
                 cpu: _T
                 ):
        """Initialize a new basic instruction"""
        self.mnemonic: str = mnemonic
        self.full_name: str = full_name
        self.operands: str = operands
        self.description: str = description
        self.operation: str = operation
        self.encoding: str = encoding
        self._cpu: _T = cpu
        self._log = self.get_logger()

    @abstractmethod
    def match(self, *args, **kwargs) -> bool:
        ...

    @abstractmethod
    def assemble(self, **kwargs):
        ...

    @abstractmethod
    def execute(self, *args, **kwargs):
        """Execute """
        ...


_I = typing.TypeVar('_I', bound=PyssemblerBasicInstruction)


class PyssemblerInstructionSet(typing.Generic[_I], LoggableMixin):
    """Base class for all instruction sets.

    An instruction set acts as an interface for converting a series of tokens
    into either a basic or pseudo instruction.
    """
    def __init__(self) -> None:
        self._basic_instrs: typing.List[_I] = []
        self._log = self.get_logger()

    def add_instruction(self, instr: _I) -> None:
        self._log.debug(f'Adding Instruction: {instr.mnemonic}...')
        self._basic_instrs.append(instr)

    def match_instruction(self, statement: TokenizedStatement) -> _I:
        mnemonic = statement.tokens[0].value

        match_exeception = None

        for instr in self._basic_instrs:
            if instr.mnemonic != mnemonic:
                continue

            try:
                instr.match(statement)
                return instr

            except AssemblerException as e:
                if match_exeception is None:
                    match_exeception = e

        # If we reached this point then matching was unsuccessful.
        if match_exeception:
            raise match_exeception

        raise AssemblerException(f'No instruction found with mnemonic "{mnemonic}"')

    def get_all_mnemonics(self) -> typing.Set[str]:
        return self.get_all_basic_mnemonics()

    def get_all_basic_mnemonics(self) -> typing.Set[str]:
        return {instr.mnemonic for instr in self._basic_instrs}

    def __iter__(self):
        yield from self._basic_instrs


class PyssemblerPseudoInstruction(ABC):
    """Base class for all pseudo instructions.

    A pseudo instruction is not explicitly a part of an architecture's
    instruction set but instead gets assembled into a series of
    basic instructions (even if it's just an alias for a single
    basic instruction).
    """

    def __init__(self, mnemonic: str):
        self.mnemonic: str = mnemonic

    @abstractmethod
    def expand(self):
        ...
