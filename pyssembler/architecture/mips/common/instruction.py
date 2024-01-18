from __future__ import annotations
from collections.abc import Iterator
from functools import cached_property
import string
import typing

from .cpu import MIPSCPU
from pyssembler.architecture import core
from pyssembler.architecture.utils import numeric
from pyssembler.architecture.mips.common import assembler_errors, mips_enums, mips_exceptions
from pyssembler.architecture.mips.common.mips_token import MIPSToken

if typing.TYPE_CHECKING:
    from pyssembler.architecture.mips.common.statement import MIPSStatement
    from pyssembler.architecture.mips.common.assembler import MIPSAssemblerContext

__all__ = [
    'MIPSBasicInstruction',
    'MIPSControlTransferInstruction',
    'MIPSCompactControlTransferInstruction',
    'MIPSBaseBranchInstruction',
    'MIPSBaseCompactBranchInstruction',
    'MIPSBaseJumpInstruction',
    'MIPSBaseCompactJumpInstruction',
    'mips_deprecated'
]


class MIPSInstructionField(typing.NamedTuple):
    value: int
    encoding_size: int
    token: MIPSToken


class MIPSBasicInstruction(core.PyssemblerBasicInstruction[MIPSCPU]):
    """Base class for all MIPS basic instructions"""
    __mips_deprecated__: bool = False
    __mips_alternatives__: typing.Tuple[typing.Type['MIPSBasicInstruction']] = tuple()

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._fmt_tokens: typing.Dict[str, mips_enums.MIPSTokenType] = {}

        # Common register names
        self._register_fmt_token('rd', mips_enums.MIPSTokenType.REGISTER)
        self._register_fmt_token('rs', mips_enums.MIPSTokenType.REGISTER)
        self._register_fmt_token('rt', mips_enums.MIPSTokenType.REGISTER)
        self._register_fmt_token('immediate', mips_enums.MIPSTokenType.IMMEDIATE_LIKE)

    @property
    def has_delay_slot(self):
        return False

    @cached_property
    def fmt_statement(self):
        return self._cpu.assembler.tokenize_text(
            self.operands,
            custom_tokens=self._fmt_tokens
        )[0]

    def match(self, statement: MIPSStatement) -> bool:
        if statement.tokens[0].value != self.mnemonic:
            return False

        if len(statement) > len(self.fmt_statement):
            raise assembler_errors.MIPSSyntaxError(
                statement.tokens[len(self.fmt_statement)],
                summary=f'Syntax Error'
            )

        # Match token-by-token
        statement_idx = 0
        prev_statement_token = statement.identifier
        for fmt_token in self.fmt_statement:
            try:
                statement_token = statement.tokens[statement_idx]
            except IndexError:
                # Statement is missing tokens
                raise assembler_errors.MIPSSyntaxError(
                    prev_statement_token,
                    summary=f'Syntax Error'
                )

            # Check that token types match
            if statement_token.type not in fmt_token.type:
                raise assembler_errors.MIPSUnexpectedTokenError(
                    statement_token,
                    fmt_token
                )

            statement_idx += 1
            prev_statement_token = statement_token

        return True

    def assemble(self, statement: MIPSStatement) -> int:
        if not self.match(statement):
            raise ValueError(f'Invalid statement')

        fields = {
            k: numeric.to_uint(v.value, size=v.encoding_size)
            for k, v in self._get_fields(statement).items()
        }

        return int(self.encoding.replace(' ', '').format(**fields), 2)

    def _register_fmt_token(self, token_str: str, token_type: mips_enums.MIPSTokenType) -> None:
        if token_str in self._fmt_tokens:
            raise ValueError(f'Token string "{token_str}" already registered!')

        self._fmt_tokens[token_str] = token_type

    def _yield_tokens(self, statement: MIPSStatement) -> Iterator[typing.Tuple[MIPSToken, MIPSToken]]:
        yield from zip(self.fmt_statement, statement)

    def _handle_immediate(self, imm: int, fmt_token: MIPSToken, statement: MIPSStatement) -> int:
        return imm

    def _get_encoding_sizes(self) -> typing.Dict[str, int]:
        fmt = string.Formatter()
        sizes = {}
        for _, name, spec, _ in fmt.parse(self.encoding):
            if name is None or spec is None:
                continue

            if 'b' not in spec:
                continue
            sizes[name] = int(spec[:-1])

        return sizes

    def _get_fields(self, statement: MIPSStatement):
        fields = {}
        field_sizes = self._get_encoding_sizes()

        for fmt_token, statement_token in self._yield_tokens(statement):
            if fmt_token.value not in field_sizes:
                continue

            value = 0
            # Immediate encoding
            if fmt_token.type in mips_enums.MIPSTokenType.IMMEDIATE_LIKE:

                # Statement token is a label, use address
                if statement_token.type == mips_enums.MIPSTokenType.LABEL:
                    # First search locally
                    local_table = statement.program.get_file_symbols(statement_token.src.asm_file)
                    if local_table.has_symbol(statement_token.value):
                        value = local_table.get_symbol(statement_token.value).address

                    # Search globally
                    elif statement.program.global_symbols.has_symbol(statement_token.value):
                        value = statement.program.global_symbols.get_symbol(statement_token.value).address

                    # Could not find label
                    else:
                        raise assembler_errors.MIPSSymbolDoesNotExist(
                            statement_token
                        )

                # Statement token should be an immediate-like value
                else:
                    value = statement_token.value

            else:
                value = statement_token.value

            fields[fmt_token.value] = MIPSInstructionField(
                self._handle_immediate(value, fmt_token, statement),
                field_sizes[fmt_token.value],
                statement_token
            )
        return fields

    def _execute_prechecks(self, statement: MIPSStatement):
        if not self.match(statement):
            raise ValueError(f'Could not execute statement: Does not match!')


class MIPSControlTransferInstruction(MIPSBasicInstruction):
    """Base class for all MIPS Control Transfer Instructions (CTIs).

    CTIs executed in the delay slot of a branch of jump will signal a
    Reserved Instruction exception.
    """

    @property
    def has_delay_slot(self):
        return True

    def _execute_prechecks(self, statement: MIPSStatement):
        super()._execute_prechecks(statement)

        # Check for CTI in the delay slot
        if self._cpu.do_delay_slots:
            delay_slot = self._cpu.get_pc_instruction(offset=1)
            if delay_slot is not None:
                if isinstance(delay_slot.instr_impl, MIPSControlTransferInstruction):
                    raise mips_exceptions.ReservedInstructionException()

    def _execute_delay_slot(self, statement: MIPSStatement) -> None:
        """Execute the instruction in a statement's delay slot."""
        if self._cpu.do_delay_slots:
            try:
                self._cpu.execute_instruction_at_address(statement.address + 4, delay_slot=True)

            # Ignore ProgramDroppedOff Exceptions: Treat Delay Slot as a no-op
            except core.ProgramDroppedOff:
                self._log.debug(f'No instruction found in delay slot: Treating as NO-OP')
                return

            # Let any other exceptions bubble up


class MIPSCompactControlTransferInstruction(MIPSControlTransferInstruction):
    @property
    def has_delay_slot(self):
        return False


class MIPSBaseBranchInstruction(MIPSControlTransferInstruction):
    """Base class for all MIPS Branch instructions.

    All Branch instructions have a delay slot.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._register_fmt_token('offset', mips_enums.MIPSTokenType.IMMEDIATE_LIKE)

    def _handle_immediate(self, imm: int, fmt_token: MIPSToken, statement: MIPSStatement) -> int:
        if fmt_token.value == 'offset':
            # A signed offset is added to the address of the instruction
            # following the branch (not the branch itself), in the branch
            # delay slot, to form a PC-relative effective target address.
            return (imm - statement.address - 4) >> 2

        return super()._handle_immediate(imm, fmt_token, statement)


class MIPSBaseCompactBranchInstruction(MIPSCompactControlTransferInstruction):
    """Base class for all MIPS Compact Branch instructions.

    Compact Branches do NOT have a delay slot.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._register_fmt_token('offset', mips_enums.MIPSTokenType.IMMEDIATE_LIKE)

    def _handle_immediate(self, imm: int, fmt_token: MIPSToken, statement: MIPSStatement) -> int:
        if fmt_token.value == 'offset':
            # A signed offset is added to the address of the instruction
            # following the branch (not the branch itself), in the branch
            # delay slot, to form a PC-relative effective target address.
            return (imm - statement.address - 4) >> 2

        return super()._handle_immediate(imm, fmt_token, statement)


class MIPSBaseJumpInstruction(MIPSControlTransferInstruction):
    """Base class for all MIPS Jump instructions.

    All Jump instructions have a delay slot.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._register_fmt_token('target', mips_enums.MIPSTokenType.IMMEDIATE_LIKE)

    def _handle_immediate(self, imm: int, fmt_token: MIPSToken, statement: MIPSStatement) -> int:
        if fmt_token.value == 'target':
            # This is a PC-region branch (not PC-relative); the effective
            # target address is in the "current" 256 MB-aligned region. The
            # low N bits of the target address is the instruction index field
            # shifted left two bits. The remaining upper bits are the
            # corresponding bits of the address of the instruction in the delay
            # slot (not the branch itself).
            return imm >> 2

        return super()._handle_immediate(imm, fmt_token, statement)


class MIPSBaseCompactJumpInstruction(MIPSCompactControlTransferInstruction):
    """Base class for all MIPS Jump instructions.

    Compact Jump instructions do not have a delay slot.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._register_fmt_token('offset', mips_enums.MIPSTokenType.IMMEDIATE_LIKE)

    def _handle_immediate(self, imm: int, fmt_token: MIPSToken, statement: MIPSStatement) -> int:
        if fmt_token.value == 'offset':
            # The jump target is formed by sign-extending the offset field of
            # instruction and adding it to the contents of a General Purpose
            # Register (GPR). The offset is NOT shifted, that is, each bit of
            # the offset is added to the corresponding bit of the GPR.
            return imm

        return super()._handle_immediate(imm, fmt_token, statement)


def mips_deprecated(
        *args: typing.Type[MIPSBasicInstruction]
) -> typing.Callable[[typing.Type[MIPSBasicInstruction]], typing.Type[MIPSBasicInstruction]]:
    """Declare that the MIPS instruction is deprecated in Release 6."""

    def decorator(instr: typing.Type[MIPSBasicInstruction]) -> typing.Type[MIPSBasicInstruction]:
        instr.__mips_deprecated__ = True
        instr.__mips_alternatives__ = args
        return instr

    return decorator
