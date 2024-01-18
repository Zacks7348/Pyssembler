from __future__ import annotations
from abc import ABC, abstractmethod
from pathlib import Path
import typing

from .assembler_errors import *
from .mips_enums import *
from .hardware.constants import MIPSMemorySize
from pyssembler.utils import LoggableMixin
from pyssembler.architecture.utils import AssemblyFile

if typing.TYPE_CHECKING:
    from .statement import MIPSStatement
    from .assembler import MIPSAssemblerContext
    from .cpu import MIPSCPU

__all__ = [
    'MIPSDirective',
    'AlignDirective',
    'AsciiDirective',
    'AsciizDirective',
    'ByteDirective',
    'DataDirective',
    'ExternDirective',
    'GloblDirective',
    'HalfDirective',
    'IncludeDirective',
    'KDataDirective',
    'KTextDirective',
    'SpaceDirective',
    'TextDirective',
    'WordDirective'
]


class _FormatToken(typing.NamedTuple):
    expected_type: MIPSTokenType
    enumeration: typing.Optional[typing.List[typing.Any]]
    occurrences: int | str


class MIPSDirective(ABC, LoggableMixin):
    """Base class for a MIPS Assembler Directive"""

    def __init__(self, name: str, description: str):
        self.name: str = name
        self.description: str = description
        self._log = self.get_logger(name=self.name)

    @property
    @abstractmethod
    def valid_segments(self) -> Segment:
        ...

    @property
    @abstractmethod
    def fmt(self) -> typing.List[_FormatToken]:
        ...

    @abstractmethod
    def execute(self, statement: MIPSStatement, ctx: MIPSAssemblerContext, cpu: MIPSCPU) -> None:
        ...

    def match(self, statement: MIPSStatement) -> bool:
        if not statement.is_directive():
            return False

        if not statement.tokens[0].value == self.name:
            return False

        self.validate(statement)
        return True

    def validate(self, statement: MIPSStatement) -> None:
        """Validate a directive statement.

        Assumes that the statement matches this directive
        """
        if statement.segment not in self.valid_segments:
            raise MIPSInvalidSegmentError(statement.tokens[0])

        fmt_tokens = self.fmt
        if not fmt_tokens:
            return

        i = 1  # Token list pointer (ignore directive token)
        j = 0  # Directive format token pointer
        k = 0  # nargs counter
        while i < len(statement.tokens):
            fmt_type, fmt_vals, fmt_nargs = fmt_tokens[j]
            if statement.tokens[i].type not in fmt_type:
                raise MIPSSyntaxError(statement.tokens[i])
            if fmt_vals:
                if statement.tokens[i].value not in fmt_vals:
                    raise MIPSSyntaxError(statement.tokens[i])
            if fmt_nargs == '+':
                i += 1
            else:
                k += 1
                if k == fmt_nargs:
                    j += 1
                i += 1

    def _add_data_symbol(self, statement: MIPSStatement, ctx: MIPSAssemblerContext):
        if statement.label is None:
            return

        symbols = statement.program.get_file_symbols(statement.src.asm_file)
        if symbols.has_symbol(statement.label.value):
            raise MIPSSymbolAlreadyExistsError(statement.label)

        symbols.add_symbol(
            statement.label.value,
            source=statement.label.src,
            address=ctx.get_next_data_ptr(statement.segment)
        )


class AlignDirective(MIPSDirective):
    """Represents the MIPS .align directive"""

    def __init__(self):
        super().__init__(
            '.align',
            'Align the next data item on a byte boundary (0=byte, 1=halfword, 2=word, 3=doubleword)')

    @property
    def valid_segments(self) -> Segment:
        return Segment.ANY_DATA

    @property
    def fmt(self) -> typing.List[_FormatToken]:
        return [
            # A single immediate
            _FormatToken(
                MIPSTokenType.IMMEDIATE_LIKE_VALUE,
                [0, 1, 2, 3],
                1
            )
        ]

    def execute(self, statement: MIPSStatement, ctx: MIPSAssemblerContext, cpu: MIPSCPU) -> None:
        value = statement.tokens[1].value

        # Memory is byte-addressed
        if value == 0:
            return

        byte_boundary = 2 ** value
        current_addr = ctx.get_next_data_ptr(segment=statement.segment)
        offset = current_addr % byte_boundary
        ctx.get_next_data_ptr(segment=statement.segment, reserved=byte_boundary - offset)


class AsciiDirective(MIPSDirective):
    """Represents the MIPS .ascii directive"""

    def __init__(self):
        super().__init__(
            '.ascii',
            'Store the string in memory without a null terminator')

    @property
    def valid_segments(self) -> Segment:
        return Segment.ANY_DATA

    @property
    def fmt(self) -> typing.List[_FormatToken]:
        return [
            # A single ASCII string
            _FormatToken(
                MIPSTokenType.ASCII,
                None,
                1
            )
        ]

    def execute(self, statement: MIPSStatement, ctx: MIPSAssemblerContext, cpu: MIPSCPU) -> None:
        self._add_data_symbol(statement, ctx)
        ascii_str = statement.tokens[1].value

        for char in ascii_str:
            addr = ctx.get_next_data_ptr(
                segment=statement.segment,
                reserved=MIPSMemorySize.BYTE_LENGTH_BYTES
            )
            if ctx.update_memory:
                cpu.memory.write_byte(
                    addr,
                    ord(char),
                    program_segment=statement.segment
                )


class AsciizDirective(MIPSDirective):
    """Represents the MIPS .asciiz directive"""

    def __init__(self):
        super().__init__(
            '.asciiz',
            'Store the string in memory with a null terminator')

    @property
    def valid_segments(self) -> Segment:
        return Segment.ANY_DATA

    @property
    def fmt(self) -> typing.List[_FormatToken]:
        return [
            # A single ASCII string
            _FormatToken(
                MIPSTokenType.ASCII,
                None,
                1
            )
        ]

    def execute(self, statement: MIPSStatement, ctx: MIPSAssemblerContext, cpu: MIPSCPU) -> None:
        self._add_data_symbol(statement, ctx)
        ascii_str = statement.tokens[1].value + '\0'

        for char in ascii_str:
            addr = ctx.get_next_data_ptr(
                segment=statement.segment,
                reserved=MIPSMemorySize.BYTE_LENGTH_BYTES
            )
            if ctx.update_memory:
                cpu.memory.write_byte(
                    addr,
                    ord(char),
                    program_segment=statement.segment
                )


class ByteDirective(MIPSDirective):
    """Represents the MIPS .byte directive"""

    def __init__(self):
        super().__init__(
            '.byte',
            'Store the listed value(s) as bytes in memory')

    @property
    def valid_segments(self) -> Segment:
        return Segment.ANY_DATA

    @property
    def fmt(self) -> typing.List[_FormatToken]:
        return [
            # 1 or more immediate values
            _FormatToken(
                MIPSTokenType.IMMEDIATE_LIKE_VALUE,
                None,
                '+'
            )
        ]

    def execute(self, statement: MIPSStatement, ctx: MIPSAssemblerContext, cpu: MIPSCPU) -> None:
        self._add_data_symbol(statement, ctx)

        for token in statement.tokens[1:]:
            addr = ctx.get_next_data_ptr(statement.segment, reserved=MIPSMemorySize.BYTE_LENGTH_BYTES)
            if ctx.update_memory:
                cpu.memory.write_byte(
                    addr,
                    token.value,
                    program_segment=statement.segment
                )


class DataDirective(MIPSDirective):
    """Represents the MIPS .data directive"""

    def __init__(self):
        super().__init__(
            '.data',
            'Declare the following statements are stored in Data memory')

    @property
    def valid_segments(self) -> Segment:
        return Segment.ALL

    @property
    def fmt(self) -> typing.List[_FormatToken]:
        return []

    def execute(self, statement: MIPSStatement, ctx: MIPSAssemblerContext, cpu: MIPSCPU) -> None:
        ctx.current_segment = Segment.DATA


class ExternDirective(MIPSDirective):
    """Represents the MIPS .extern directive"""

    def __init__(self):
        super().__init__(
            '.extern',
            'Declare the label and byte length as a global data field')

    @property
    def valid_segments(self) -> Segment:
        return Segment.ALL

    @property
    def fmt(self) -> typing.List[_FormatToken]:
        return [
            # Label to identify byte range
            _FormatToken(
                MIPSTokenType.LABEL,
                None,
                1
            ),
            # Number of bytes
            _FormatToken(
                MIPSTokenType.IMMEDIATE_LIKE_VALUE,
                None,
                1
            )
        ]

    def execute(self, statement: MIPSStatement, ctx: MIPSAssemblerContext, cpu: MIPSCPU) -> None:
        symbol = statement.tokens[1]
        if ctx.globl_symbols.has_symbol(symbol.value):
            raise MIPSSymbolAlreadyExistsError(symbol)
        ctx.globl_symbols.add_symbol(
            symbol.value,
            source=symbol.src,
            address=ctx.get_next_data_ptr(segment=statement.segment, reserved=statement.tokens[2].value)
        )


class GloblDirective(MIPSDirective):
    """Represents the MIPS .globl directive"""

    def __init__(self):
        super().__init__(
            '.globl',
            'Declare the label(s) as global')

    @property
    def valid_segments(self) -> Segment:
        return Segment.ALL

    @property
    def fmt(self) -> typing.List[_FormatToken]:
        return [
            _FormatToken(
                MIPSTokenType.LABEL,
                None,
                1
            )
        ]

    def execute(self, statement: MIPSStatement, ctx: MIPSAssemblerContext, cpu: MIPSCPU) -> None:
        for symbol in statement.tokens[1:]:
            ctx.global_symbol_list.append(symbol)


class HalfDirective(MIPSDirective):
    """Represents the MIPS .half directive"""

    def __init__(self):
        super().__init__(
            '.half',
            'Store the listed value(s) as half-words in memory')

    @property
    def valid_segments(self) -> Segment:
        return Segment.ANY_DATA

    @property
    def fmt(self) -> typing.List[_FormatToken]:
        return [
            # 1 or more immediate values
            _FormatToken(
                MIPSTokenType.IMMEDIATE_LIKE_VALUE,
                None,
                '+'
            )
        ]

    def execute(self, statement: MIPSStatement, ctx: MIPSAssemblerContext, cpu: MIPSCPU) -> None:
        self._add_data_symbol(statement, ctx)

        for token in statement.tokens[1:]:
            addr = ctx.get_next_data_ptr(statement.segment, reserved=MIPSMemorySize.HWORD_LENGTH_BYTES)
            if ctx.update_memory:
                cpu.memory.write_halfword(
                    addr,
                    token.value,
                    program_segment=statement.segment
                )


class IncludeDirective(MIPSDirective):
    """Represents the MIPS .include directive"""

    def __init__(self):
        super().__init__(
            '.include',
            'Insert the contents of a file starting at location of the directive')

    @property
    def valid_segments(self) -> Segment:
        return Segment.ALL

    @property
    def fmt(self) -> typing.List[_FormatToken]:
        return [
            # 1 or more immediate values
            _FormatToken(
                MIPSTokenType.ASCII,
                None,
                1
            )
        ]

    def execute(self, statement: MIPSStatement, ctx: MIPSAssemblerContext, cpu: MIPSCPU) -> None:
        if not ctx.process_includes:
            return

        file_token = statement.tokens[1]
        included_file = Path(file_token.value)
        # Add .asm suffix if not present
        if included_file.suffix is None:
            included_file = included_file.with_suffix('.asm')

        # Resolve relative to source file
        included_file = (statement.tokens[0].src_file.path.parent / included_file).resolve()
        if not included_file.is_file():
            raise MIPSIncludeError(file_token, 'Not a file!')

        # Defend against circular includes
        if included_file in ctx.seen_files:
            raise MIPSIncludeError(file_token, 'Circular include detected!')
        ctx.seen_files.add(included_file)
        asm_file = AssemblyFile(included_file)

        try:
            # Tokenize the included file
            tokenized_statements = ctx.assembler.tokenize_text(
                asm_file.text(),
                asm_file=asm_file,
            )

            # Assemble tokenized statements into full MIPS statements
            ctx.assembler.assemble_from_tokens(
                tokenized_statements
            )
        except MIPSAssemblerError as e:
            raise MIPSIncludeError(file_token, f'An error occurred during include:\n{e.error_msg}')


class KDataDirective(MIPSDirective):
    """Represents the MIPS .kdata directive"""

    def __init__(self):
        super().__init__(
            '.kdata',
            'Declare the following statements are stored in Kernel Data memory')

    @property
    def valid_segments(self) -> Segment:
        return Segment.ALL

    @property
    def fmt(self) -> typing.List[_FormatToken]:
        return []

    def execute(self, statement: MIPSStatement, ctx: MIPSAssemblerContext, cpu: MIPSCPU) -> None:
        ctx.current_segment = Segment.KDATA


class KTextDirective(MIPSDirective):
    """Represents the MIPS .ktext directive"""

    def __init__(self):
        super().__init__(
            '.ktext',
            'Declare the following statements are stored in Kernel Text memory')

    @property
    def valid_segments(self) -> Segment:
        return Segment.ALL

    @property
    def fmt(self) -> typing.List[_FormatToken]:
        return []

    def execute(self, statement: MIPSStatement, ctx: MIPSAssemblerContext, cpu: MIPSCPU) -> None:
        ctx.current_segment = Segment.KTEXT


class SpaceDirective(MIPSDirective):
    """Represents the MIPS .space directive"""

    def __init__(self):
        super().__init__(
            '.space',
            'Declare the byte length as a local data field')

    @property
    def valid_segments(self) -> Segment:
        return Segment.ALL

    @property
    def fmt(self) -> typing.List[_FormatToken]:
        return [
            # A single immediate
            _FormatToken(
                MIPSTokenType.IMMEDIATE,
                None,
                1
            )
        ]

    def execute(self, statement: MIPSStatement, ctx: MIPSAssemblerContext, cpu: MIPSCPU) -> None:
        if not ctx.update_memory:
            return

        raise NotImplementedError()


class WordDirective(MIPSDirective):
    """Represents the MIPS .word directive"""

    def __init__(self):
        super().__init__(
            '.word',
            'Store the listed value(s) as words in memory')

    @property
    def valid_segments(self) -> Segment:
        return Segment.ANY_DATA

    @property
    def fmt(self) -> typing.List[_FormatToken]:
        return [
            # 1 or more immediate values
            _FormatToken(
                MIPSTokenType.IMMEDIATE_LIKE_VALUE,
                None,
                '+'
            )
        ]

    def execute(self, statement: MIPSStatement, ctx: MIPSAssemblerContext, cpu: MIPSCPU) -> None:
        self._add_data_symbol(statement, ctx)

        for token in statement.tokens[1:]:
            addr = ctx.get_next_data_ptr(statement.segment, reserved=MIPSMemorySize.WORD_LENGTH_BYTES)
            if ctx.update_memory:
                cpu.memory.write_word(
                    addr,
                    token.value,
                    program_segment=statement.segment
                )


class TextDirective(MIPSDirective):
    """Represents the MIPS .text directive"""

    def __init__(self):
        super().__init__(
            '.text',
            'Declare the following statements are stored in Text memory')

    @property
    def valid_segments(self) -> Segment:
        return Segment.ALL

    @property
    def fmt(self) -> typing.List[_FormatToken]:
        return []

    def execute(self, statement: MIPSStatement, ctx: MIPSAssemblerContext, cpu: MIPSCPU) -> None:
        ctx.current_segment = Segment.TEXT
