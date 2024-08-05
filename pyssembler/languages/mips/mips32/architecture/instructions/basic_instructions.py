from __future__ import annotations
import typing

from .instruction_set import mips32_instruction
from pyssembler.languages.mips.common.architecture import mips_exceptions, mips_enums
from pyssembler.languages.mips.common.architecture.instruction import *
from pyssembler.languages.mips.common.architecture.hardware import constants
from pyssembler.utils import numeric

if typing.TYPE_CHECKING:
    from ..cpu import MIPS32CPU
    from pyssembler.languages.mips.common.architecture.statement import MIPSStatement
    from pyssembler.languages.mips.common.architecture.mips_token import MIPSToken


@mips32_instruction
class MIPS32AddInstruction(MIPSBasicInstruction):
    def __init__(self, cpu: MIPS32CPU, **kwargs):
        super().__init__(
            'add',
            'Add Word',
            'add rd, rs, rt',
            'Add 32-bit integers (trap on overflow)',
            'GPR[rd] = GPR[rs] + GPR[rt]',
            '000000 {rs:05b} {rt:05b} {rd:05b} 00000 100000',
            cpu,
            **kwargs
        )

    def execute(self, statement: MIPSStatement) -> None:
        """Add 32-bit integers. If an overflow occurs, trap."""
        self._execute_prechecks(statement)
        fields = self._get_fields(statement)

        # The 32-bit word value in GPR[rt] is added to the 32-bit value in
        # GPR[rs] to produce a 32-bit result.
        rd_address = fields['rd'].value

        rs_address = fields['rs'].value
        rs_value = self._cpu.gpr.read_integer(addr=rs_address, signed=True)

        rt_address = fields['rt'].value
        rt_value = self._cpu.gpr.read_integer(addr=rt_address, signed=True)

        res = numeric.to_int(rs_value + rt_value, size=constants.MIPSMemorySize.WORD)

        # If the addition results in 32-bit 2's compliment arithmetic overflow,
        # the destination register is not modified and an Integer Overflow
        # exception occurrs.
        if numeric.detect_overflow(rs_value, rt_value, res):
            raise mips_exceptions.ArithmeticOverflowException()

        # If the addition does not overflow, the 32-bit result is placed into GPR[rd]
        self._cpu.gpr.write_integer(res, addr=rd_address)


@mips32_instruction
class MIPS32AddiuInstruction(MIPSBasicInstruction):
    def __init__(self, cpu: MIPS32CPU, **kwargs):
        super().__init__(
            'addiu',
            'Add Immediate Unsigned Word',
            'addiu rt, rs, immediate',
            'Add a constant to a 32-bit integer',
            'GPR[rt] = GPR[rs] + sign_extend(immediate)',
            '001001 {rs:05b} {rt:05b} {immediate:016b}',
            cpu,
            **kwargs
        )

    def execute(self, statement: MIPSStatement) -> None:
        """Add a constant to a 32-bit integer."""
        self._execute_prechecks(statement)
        fields = self._get_fields(statement)

        # The 16-bit signed immediate is added to the 32-bit value in GPR[rs]
        imm = numeric.to_int(fields['immediate'].value, size=constants.MIPSMemorySize.WORD)

        rs_address = fields['rs'].value
        rs_value = self._cpu.gpr.read_integer(addr=rs_address, signed=True)

        rt_address = fields['rt'].value

        res = numeric.to_int(rs_value + imm, size=constants.MIPSMemorySize.WORD)

        # The 32-bit arithmetic result is placed into GPR[rt]
        self._cpu.gpr.write_integer(res, addr=rt_address)


@mips32_instruction
class MIPS32AddiupcInstruction(MIPSBasicInstruction):
    def __init__(self, cpu: MIPS32CPU, **kwargs):
        super().__init__(
            'addiupc',
            'Add Immediate to PC (unsigned, non-trapping)',
            'addiupc rs, immediate',
            'Perform a PC-relative address calculation',
            'GPR[rs] = PC + sign_extend(immediate << 2)',
            '111011 {rs:05b} 00 {immediate:019b}',
            cpu,
            **kwargs
        )

    def execute(self, statement: MIPSStatement) -> None:
        """Perform a PC-relative address calculation."""
        self._execute_prechecks(statement)
        fields = self._get_fields(statement)

        # The 19-bit signed immediate is shifted left by two bits, sign-extended,
        # and added to the address of the ADDIUPC instruction.
        imm = numeric.to_int(fields['immediate'].value << 2, size=constants.MIPSMemorySize.WORD)

        rs_address = fields['rs'].value

        res = numeric.to_int(self._cpu.pc.read_integer() + imm, size=constants.MIPSMemorySize.WORD)

        # The 32-bit arithmetic result is placed into GPR[rs]
        self._cpu.gpr.write_integer(res, addr=rs_address)


@mips32_instruction
class MIPS32AdduInstruction(MIPSBasicInstruction):
    def __init__(self, cpu: MIPS32CPU, **kwargs):
        super().__init__(
            'addu',
            'Add Unsigned Word',
            'addu, rd, rs, rt',
            'Add 32-bit integers',
            'GPR[rd] = GPR[rs] + GPR[rt]',
            '000000 {rs:05b} {rt:05b} {rd:05b} 00000 100001',
            cpu,
            **kwargs
        )

    def execute(self, statement: MIPSStatement) -> None:
        """Add 32-bit integers."""
        self._execute_prechecks(statement)
        fields = self._get_fields(statement)

        # The 32-bit word value in GPR[rt] is added to the 32-bit value in
        # GPR[rs]...
        rd_address = fields['rd'].value

        rs_address = fields['rs'].value
        rs_value = self._cpu.gpr.read_integer(addr=rs_address, signed=True)

        rt_address = fields['rt'].value
        rt_value = self._cpu.gpr.read_integer(addr=rt_address, signed=True)

        res = numeric.to_int(rs_value + rt_value, size=constants.MIPSMemorySize.WORD)

        # ...the 32-bit arithmetic result is placed into GPR[rd]
        self._cpu.gpr.write_integer(res, addr=rd_address)


@mips32_instruction
class MIPS32AlignInstruction(MIPSBasicInstruction):
    def __init__(self, cpu: MIPS32CPU, **kwargs):
        super().__init__(
            'align',
            'Align',
            'align rd, rs, rt, bp',
            'Concatenate two GPRs and extract a contiguous subset at a byte position',
            'GPR[rd] = (GPR[rt] << (8 * bp)) or (GPR[rs] >> (GPRLEN - 8 * bp)))',
            '011111 {rs:05b} {rt:05b} {rd:05b} 010 {bp:02b} 100000',
            cpu,
            **kwargs
        )
        self._register_fmt_token('bp', mips_enums.MIPSTokenType.IMMEDIATE_LIKE_VALUE)

    def execute(self, statement: MIPSStatement) -> None:
        """Concatenate two GPRs and extract a contiguous subset at a byte position."""
        self._execute_prechecks(statement)
        fields = self._get_fields(statement)

        # The input registers GPR[rt] and GPR[rs] are concatenated,
        # and a register width continuous subset is extracted, which is
        # specified by the byte pointer bp.
        bp = fields['bp'].value * constants.MIPSMemorySize.BYTE

        # The 32-bit word in GPR[rt] is left shifted as a 32-bit value
        # by bp byte positions (logical shift, zero-filling).
        rt_address = fields['rt'].value
        rt_value = numeric.to_uint(
            self._cpu.gpr.read_integer(addr=rt_address) << bp,
            size=constants.MIPSMemorySize.WORD
        )

        # The 32-bit word in GPR[rs] is right shifted as a 32-bit value
        # by (4-bp) positions (logical shift, zero-filling).
        rs_address = fields['rs'].value
        rs_value = numeric.to_uint(
            self._cpu.gpr.read_integer(addr=rs_address) >> (constants.MIPSMemorySize.WORD_LENGTH_BYTES - bp),
            size=constants.MIPSMemorySize.WORD
        )

        # The shifted values are then or-ed together to crease a 32-bit
        # result that is written to destination GPR[rd].
        res = numeric.to_uint(rt_value | rs_value, size=constants.MIPSMemorySize.WORD)

        rd_address = fields['rd'].value

        self._cpu.gpr.write_integer(res, addr=rd_address)


@mips32_instruction
class MIPS32AluipcInstruction(MIPSBasicInstruction):
    def __init__(self, cpu: MIPS32CPU, **kwargs):
        super().__init__(
            'aluipc',
            'Aligned Add Upper Immediate to PC',
            'aluipc, rs, immediate',
            'Perform a PC-relative address calculation',
            'GPR[rs] = ~0x0FFFF and (PC + sign_extend(immediate << 16))',
            '111011 {rs:05b 11111 {immediate:016b}}',
            cpu,
            **kwargs
        )

    def execute(self, statement: MIPSStatement) -> None:
        """Aligned Add Upper Immediate to PC."""
        self._execute_prechecks(statement)
        fields = self._get_fields(statement)

        # The 16-bit immediate is shifted left by 16 bits,
        # sign_extended, and added to the address of the ALUIPC instruction.
        imm = numeric.to_int(fields['immediate'].value << 16, size=constants.MIPSMemorySize.WORD)

        res = statement.address + imm

        # The low 16 bits of the result are cleared, that is the result is
        # aligned on a 64K boundary.
        res &= ~0x0FFFF

        # The result is placed in GPR[rs]
        rs_address = fields['rs'].value

        self._cpu.gpr.write_integer(res, addr=rs_address)


@mips32_instruction
class MIPS32AndInstruction(MIPSBasicInstruction):
    def __init__(self, cpu: MIPS32CPU, **kwargs):
        super().__init__(
            'and',
            'And',
            'and, rd, rs, rt',
            'Bitwise logical AND',
            'GPR[rd] = GPR[rs] and GPR[rt]',
            '000000 {rs:05b} {rt:05b} {rd:05b} 00000 100100',
            cpu,
            **kwargs
        )

    def execute(self, statement: MIPSStatement) -> None:
        """Bitwise logical AND."""
        self._execute_prechecks(statement)
        fields = self._get_fields(statement)

        # The contents of GPR[rs] are combined with the contents of GPR[rt]
        # in a bitwise logical AND operation.
        rs_address = fields['rs'].value
        rs_value = self._cpu.gpr.read_integer(addr=rs_address)

        rt_address = fields['rt'].value
        rt_value = self._cpu.gpr.read_integer(addr=rt_address)

        res = numeric.to_uint(rs_value & rt_value, size=constants.MIPSMemorySize.WORD)

        # The result is placed into GPR[rd].
        rd_address = fields['rd'].value

        self._cpu.gpr.write_integer(res, addr=rd_address)


@mips32_instruction
class MIPS32AndiInstruction(MIPSBasicInstruction):
    def __init__(self, cpu: MIPS32CPU, **kwargs):
        super().__init__(
            'andi',
            'And Immediate',
            'andi rt, rs, immediate',
            'Bitwise logical AND with a constant',
            'GPR[rt] = GPR[rs] and zero_extend(immediate)',
            '001100 {rs:05b} {rt:05b} {immediate:016b}',
            cpu,
            **kwargs
        )

    def execute(self, statement: MIPSStatement) -> None:
        """Bitwise logical AND with a constant."""
        self._execute_prechecks(statement)
        fields = self._get_fields(statement)

        # The 16-bit immediate is zero_extended to the left and combined with
        # the contents of GPR[rs] in a bitwise logical AND operation.
        rs_address = fields['rs'].value
        rs_value = self._cpu.gpr.read_integer(addr=rs_address)

        imm = numeric.to_uint(fields['immediate'].value, size=constants.MIPSMemorySize.WORD)

        res = numeric.to_uint(rs_value & imm, size=constants.MIPSMemorySize.WORD)

        # The result is placed into GPR[rt].
        rt_address = fields['rt'].value

        self._cpu.gpr.write_integer(res, addr=rt_address)


@mips32_instruction
class MIPS32AuiInstruction(MIPSBasicInstruction):
    def __init__(self, cpu: MIPS32CPU, **kwargs):
        super().__init__(
            'aui',
            'Add Upper Immediate',
            'aui rt, rs, immediate',
            'Add immediate to upper bits',
            'GPR[rt] = GPR[rs] + sign_extend(immediate << 16)',
            '001111 {rs:05b} {rt:05b} {immediate:016b}',
            cpu,
            **kwargs
        )

    def execute(self, statement: MIPSStatement) -> None:
        """Add immediate to upper bits."""
        self._execute_prechecks(statement)
        fields = self._get_fields(statement)

        # the 16-bit immediate is shifted left 16 bits, sign-extended, and
        # added to the register GPR[rs]...
        imm = numeric.to_int(fields['immediate'].value << 16, size=constants.MIPSMemorySize.WORD)

        rs_address = fields['rs'].value
        rs_value = self._cpu.gpr.read_integer(addr=rs_address, signed=True)

        res = rs_value + imm

        # ...storing the result in GPR[rt]
        rt_address = fields['rt'].value
        self._cpu.gpr.write_integer(res, addr=rt_address)


@mips32_instruction
class MIPS32AuipcInstruction(MIPSBasicInstruction):
    def __init__(self, cpu: MIPS32CPU, **kwargs):
        super().__init__(
            'auipc',
            'Add Upper Immediate to PC',
            'auipc rs, immediate',
            'Perform a PC-relative address calculation',
            'GPR[rt] = PC + (immediate << 16)',
            '111011 {rs:05b} 11110 {immediate:016b}',
            cpu,
            **kwargs
        )

    def execute(self, statement: MIPSStatement) -> None:
        """Add Upper Immediate to PC."""
        self._execute_prechecks(statement)
        fields = self._get_fields(statement)

        # the 16-bit immediate is shifted left 16 bits, sign-extended, and
        # added to the address of this instruction...
        imm = numeric.to_int(fields['immediate'].value << 16, size=constants.MIPSMemorySize.WORD)

        pc = self._cpu.pc.read_integer(signed=True)

        res = pc + imm

        # ...storing the result in GPR[rs]
        rs_address = fields['rs'].value
        self._cpu.gpr.write_integer(res, addr=rs_address)


@mips32_instruction
class MIPS32BalInstruction(MIPSBaseBranchInstruction):
    def __init__(self, cpu: MIPS32CPU, **kwargs):
        super().__init__(
            'bal',
            'Branch and Link',
            'bal offset',
            'Do an unconditional PC-relative procedure call and link',
            'branch',
            '000001 00000 10001 {offset:016b}',
            cpu,
            **kwargs
        )

    def execute(self, statement: MIPSStatement) -> None:
        """Do an unconditional PC-relative procedure call."""
        self._execute_prechecks(statement)
        fields = self._get_fields(statement)

        # Place the return address link in GPR[31]. The return link is the
        # address of the second instruction following the branch,
        # where execution continues after a procedure call.
        pc = self._cpu.pc.read_integer()

        # [Pyssembler] if the CPU is not running with delay slots enabled then
        # the return link is the address of the instruction immediately
        # following the branch, where execution continues after a procedure call.
        if not self._cpu.do_delay_slots:
            pc += constants.MIPSMemorySize.WORD_LENGTH_BYTES

        else:
            pc += constants.MIPSMemorySize.WORD_LENGTH_BYTES * 2

        # Execute Delay Slot before updating any registers
        self._execute_delay_slot(statement)

        self._cpu.gpr.write_integer(pc, addr=31)

        # An 18-bit signed offset (the 16-bit offset field shifted left 2 bits)
        # is added to the address of the instruction following the branch
        # (not the branch itself), in the delay slot, to form a PC-relative effective target address.
        offset = fields['offset'] << 2
        self._cpu.pc.write_integer(pc + offset)


@mips32_instruction
class MIPS32BalcInstruction(MIPSBaseCompactBranchInstruction):
    def __init__(self, cpu: MIPS32CPU, **kwargs):
        super().__init__(
            'balc',
            'Branch and Link, Compact',
            'balc offset',
            'Do an unconditional PC-relative procedure call and link',
            'branch',
            '111010 {offset:026b}',
            cpu,
            **kwargs
        )

    def execute(self, statement: MIPSStatement) -> None:
        """Do an unconditional PC-relative procedure call."""
        self._execute_prechecks(statement)
        fields = self._get_fields(statement)

        # Place the return address link in GPR[31]. The return link is the
        # address of the instruction immediately following the branch,
        # where execution continues after a procedure call.
        pc = self._cpu.pc.read_integer()
        self._cpu.gpr.write_integer(
            pc + constants.MIPSMemorySize.WORD_LENGTH_BYTES,
            addr=31
        )

        # A 28-bit signed offset (the 26-bit offset field shifted left 2 bits)
        # is added to the address of the instruction following the branch
        # (not the branch itself), to form a PC-relative effective target address.
        offset = fields['offset'] << 2
        self._cpu.pc.write_integer(pc + offset + 4)


@mips32_instruction
class MIPS32BcInstruction(MIPSBaseCompactBranchInstruction):
    def __init__(self, cpu: MIPS32CPU, **kwargs):
        super().__init__(
            'bc',
            'Branch, Compact',
            'bc offset',
            'Do an unconditional PC-relative procedure call',
            'branch',
            '110010 {offset:026b}',
            cpu,
            **kwargs
        )

    def execute(self, statement: MIPSStatement) -> None:
        """Do an unconditional PC-relative procedure call."""
        self._execute_prechecks(statement)
        fields = self._get_fields(statement)

        # A 28-bit signed offset (the 26-bit offset field shifted left 2 bits)
        # is added to the address of the instruction following the branch
        # (not the branch itself), to form a PC-relative effective target address.
        offset = fields['offset'] << 2

        pc = self._cpu.pc.read_integer()

        self._cpu.pc.write_integer(pc + offset + 4)


@mips32_instruction
class MIPS32BeqInstruction(MIPSBaseBranchInstruction):
    def __init__(self, cpu: MIPS32CPU, **kwargs):
        super().__init__(
            'beq',
            'Branch on Equal',
            'beq rs, rt, offset',
            'Branch if contents of registers are equal',
            'if GPR[rs] == GPR[rt] then branch',
            '000100 {rs:05b} {rt:05b} {offset:016b}',
            cpu,
            **kwargs
        )

    def execute(self, statement: MIPSStatement) -> None:
        """Compare GPRs then do a PC-relative conditional branch."""
        self._execute_prechecks(statement)
        fields = self._get_fields(statement)

        # An 18-bit signed offset (the 16-bit offset field shifted left 2-bits)
        # is added to the address of the instruction following the branch (not
        # the branch itself), in the branch delay slot, to form a PC-relative
        # target address.
        offset = numeric.to_int(fields['offset'].value << 2, size=constants.MIPSMemorySize.WORD)

        rs_address = fields['rs'].value
        rs_value = self._cpu.gpr.read_integer(addr=rs_address)

        rt_address = fields['rt'].value
        rt_value = self._cpu.gpr.read_integer(addr=rt_address)

        # If the contents of GPR[rs] and GPR[rt] are not equal, branch to
        # the effective target address after the instruction in the delay slot
        # is executed.
        self._execute_delay_slot(statement)

        if rs_value == rt_value:
            pc = self._cpu.pc.read_integer()
            self._cpu.pc.write_integer(pc + offset)


@mips32_instruction
class MIPS32BgezInstruction(MIPSBaseBranchInstruction):
    def __init__(self, cpu: MIPS32CPU, **kwargs):
        super().__init__(
            'bgez',
            'Branch on Greater Than or Equal to Zero',
            'bgez rs, offset',
            'Branch if GPR[rs] is greater than or equal to zero',
            'if GPR[rs] >= GPR[0] then branch',
            '000001 {rs:05b} 00001 {offset:016b}',
            cpu,
            **kwargs
        )

    def execute(self, statement: MIPSStatement) -> None:
        """Compare GPRs then do a PC-relative conditional branch."""
        self._execute_prechecks(statement)
        fields = self._get_fields(statement)

        # An 18-bit signed offset (the 16-bit offset field shifted left 2-bits)
        # is added to the address of the instruction following the branch (not
        # the branch itself), in the branch delay slot, to form a PC-relative
        # target address.
        offset = numeric.to_int(fields['offset'].value << 2, size=constants.MIPSMemorySize.WORD)

        rs_address = fields['rs'].value
        rs_value = self._cpu.gpr.read_integer(addr=rs_address, signed=True)

        # If the contents of GPR[rs] are greater than or equal to zero (sign bit is 0), branch to
        # the effective target address after the instruction in the delay slot
        # is executed.
        self._execute_delay_slot(statement)

        if rs_value >= self._cpu.gpr.read_integer(addr=0):
            pc = self._cpu.pc.read_integer()
            self._cpu.pc.write_integer(pc + offset)


@mips32_instruction
class MIPS32BlezalcInstruction(MIPSBaseCompactBranchInstruction):
    def __init__(self, cpu: MIPS32CPU, **kwargs):
        super().__init__(
            'blezalc',
            'Branch Less Than or Equal to Zero, Compact',
            'blezalc rt, offset',
            'Compact Branch and link if GPR[rt] is less than or equal to zero',
            'if GPR[rt] <= 0, branch',
            '000110 00000 {rt:05b} {offset:016b}',
            cpu,
            **kwargs
        )

    def execute(self, statement: MIPSStatement) -> None:
        """Do an unconditional PC-relative procedure call."""
        self._execute_prechecks(statement)
        fields = self._get_fields(statement)

        # The condition is evaluated. If the condition is True,
        # the branch is taken.
        rt_address = fields['rt'].value
        rt_value = self._cpu.gpr.read_integer(addr=rt_address, signed=True)
        condition = rt_value <= self._cpu.gpr.read_integer(addr=0)

        # Place the return address link in GPR[31]. The return link is the
        # address of the instruction immediately following the branch, where
        # execution continues after a procedure call.
        # The return address link is unconditionally updated.
        self._cpu.gpr.write_integer(
            self._cpu.pc.read_integer() + 4,
            addr=31
        )

        # An 18-bit signed offset (the 16-bit offset field shifted left 2 bits)
        # is added to the address of the instruction following the branch
        # (not the branch itself), to form a PC-relative effective target address.
        if condition:
            offset = fields['offset'] << 2

            pc = self._cpu.pc.read_integer()

            self._cpu.pc.write_integer(pc + offset + 4)

    def _handle_immediate(self, imm: int, fmt_token: MIPSToken, statement: MIPSStatement) -> int:
        # rt is not allowed to be zero
        if fmt_token.value == 'rt':
            # TODO: Better error handling
            if imm == 0:
                raise mips_exceptions.ReservedInstructionException()

        return super()._handle_immediate(imm, fmt_token, statement)


@mips32_instruction
class MIPS32BgezalcInstruction(MIPSBaseCompactBranchInstruction):
    def __init__(self, cpu: MIPS32CPU, **kwargs):
        super().__init__(
            'bgezalc',
            'Branch Greater Than or Equal to Zero, Compact',
            'blezalc rt, offset',
            'Compact Branch and link if GPR[rt] is greater than or equal to zero',
            'if GPR[rt] >= 0, branch',
            '000110 {rt:05b} {rt:05b} {offset:016b}',
            cpu,
            **kwargs
        )

    def execute(self, statement: MIPSStatement) -> None:
        """Do an unconditional PC-relative procedure call."""
        self._execute_prechecks(statement)
        fields = self._get_fields(statement)

        # The condition is evaluated. If the condition is True,
        # the branch is taken.
        rt_address = fields['rt'].value
        rt_value = self._cpu.gpr.read_integer(addr=rt_address, signed=True)
        condition = rt_value >= self._cpu.gpr.read_integer(addr=0)

        # Place the return address link in GPR[31]. The return link is the
        # address of the instruction immediately following the branch, where
        # execution continues after a procedure call.
        # The return address link is unconditionally updated.
        self._cpu.gpr.write_integer(
            self._cpu.pc.read_integer() + 4,
            addr=31
        )

        # An 18-bit signed offset (the 16-bit offset field shifted left 2 bits)
        # is added to the address of the instruction following the branch
        # (not the branch itself), to form a PC-relative effective target address.
        if condition:
            offset = fields['offset'] << 2

            pc = self._cpu.pc.read_integer()

            self._cpu.pc.write_integer(pc + offset + 4)

    def _handle_immediate(self, imm: int, fmt_token: MIPSToken, statement: MIPSStatement) -> int:
        # rt is not allowed to be zero
        if fmt_token.value == 'rt':
            # TODO: Better error handling
            if imm == 0:
                raise mips_exceptions.ReservedInstructionException()

        return super()._handle_immediate(imm, fmt_token, statement)


@mips32_instruction
class MIPS32BgtzalcInstruction(MIPSBaseCompactBranchInstruction):
    def __init__(self, cpu: MIPS32CPU, **kwargs):
        super().__init__(
            'bgtzalc',
            'Branch Greater Than Zero, Compact',
            'bgtzalc rt, offset',
            'Compact Branch and link if GPR[rt] is greater than zero',
            'if GPR[rt] > 0, branch',
            '000111 00000 {rt:05b} {offset:016b}',
            cpu,
            **kwargs
        )

    def execute(self, statement: MIPSStatement) -> None:
        """Do an unconditional PC-relative procedure call."""
        self._execute_prechecks(statement)
        fields = self._get_fields(statement)

        # The condition is evaluated. If the condition is True,
        # the branch is taken.
        rt_address = fields['rt'].value
        rt_value = self._cpu.gpr.read_integer(addr=rt_address, signed=True)
        condition = rt_value > self._cpu.gpr.read_integer(addr=0)

        # Place the return address link in GPR[31]. The return link is the
        # address of the instruction immediately following the branch, where
        # execution continues after a procedure call.
        # The return address link is unconditionally updated.
        self._cpu.gpr.write_integer(
            self._cpu.pc.read_integer() + 4,
            addr=31
        )

        # An 18-bit signed offset (the 16-bit offset field shifted left 2 bits)
        # is added to the address of the instruction following the branch
        # (not the branch itself), to form a PC-relative effective target address.
        if condition:
            offset = fields['offset'] << 2

            pc = self._cpu.pc.read_integer()

            self._cpu.pc.write_integer(pc + offset + 4)

    def _handle_immediate(self, imm: int, fmt_token: MIPSToken, statement: MIPSStatement) -> int:
        # rt is not allowed to be zero
        if fmt_token.value == 'rt':
            # TODO: Better error handling
            if imm == 0:
                raise mips_exceptions.ReservedInstructionException()

        return super()._handle_immediate(imm, fmt_token, statement)


@mips32_instruction
class MIPS32BltzalcInstruction(MIPSBaseCompactBranchInstruction):
    def __init__(self, cpu: MIPS32CPU, **kwargs):
        super().__init__(
            'bltzalc',
            'Branch Less Than Zero, Compact',
            'bltzalc rt, offset',
            'Compact Branch and link if GPR[rt] is less than zero',
            'if GPR[rt] < 0, branch',
            '000111 {rt:05b} {rt:05b} {offset:016b}',
            cpu,
            **kwargs
        )

    def execute(self, statement: MIPSStatement) -> None:
        """Do an unconditional PC-relative procedure call."""
        self._execute_prechecks(statement)
        fields = self._get_fields(statement)

        # The condition is evaluated. If the condition is True,
        # the branch is taken.
        rt_address = fields['rt'].value
        rt_value = self._cpu.gpr.read_integer(addr=rt_address, signed=True)
        condition = rt_value < self._cpu.gpr.read_integer(addr=0)

        # Place the return address link in GPR[31]. The return link is the
        # address of the instruction immediately following the branch, where
        # execution continues after a procedure call.
        # The return address link is unconditionally updated.
        self._cpu.gpr.write_integer(
            self._cpu.pc.read_integer() + 4,
            addr=31
        )

        # An 18-bit signed offset (the 16-bit offset field shifted left 2 bits)
        # is added to the address of the instruction following the branch
        # (not the branch itself), to form a PC-relative effective target address.
        if condition:
            offset = fields['offset'] << 2

            pc = self._cpu.pc.read_integer()

            self._cpu.pc.write_integer(pc + offset + 4)

    def _handle_immediate(self, imm: int, fmt_token: MIPSToken, statement: MIPSStatement) -> int:
        # rt is not allowed to be zero
        if fmt_token.value == 'rt':
            # TODO: Better error handling
            if imm == 0:
                raise mips_exceptions.ReservedInstructionException()

        return super()._handle_immediate(imm, fmt_token, statement)


@mips32_instruction
class MIPS32BeqzalcInstruction(MIPSBaseCompactBranchInstruction):
    def __init__(self, cpu: MIPS32CPU, **kwargs):
        super().__init__(
            'beqzalc',
            'Branch Equal To Zero, Compact',
            'beqzalc rt, offset',
            'Compact Branch and link if GPR[rt] is equal to zero',
            'if GPR[rt] == 0, branch',
            '001000 00000 {rt:05b} {offset:016b}',
            cpu,
            **kwargs
        )

    def execute(self, statement: MIPSStatement) -> None:
        """Do an unconditional PC-relative procedure call."""
        self._execute_prechecks(statement)
        fields = self._get_fields(statement)

        # The condition is evaluated. If the condition is True,
        # the branch is taken.
        rt_address = fields['rt'].value
        rt_value = self._cpu.gpr.read_integer(addr=rt_address, signed=True)
        condition = rt_value == self._cpu.gpr.read_integer(addr=0)

        # Place the return address link in GPR[31]. The return link is the
        # address of the instruction immediately following the branch, where
        # execution continues after a procedure call.
        # The return address link is unconditionally updated.
        self._cpu.gpr.write_integer(
            self._cpu.pc.read_integer() + 4,
            addr=31
        )

        # An 18-bit signed offset (the 16-bit offset field shifted left 2 bits)
        # is added to the address of the instruction following the branch
        # (not the branch itself), to form a PC-relative effective target address.
        if condition:
            offset = fields['offset'] << 2

            pc = self._cpu.pc.read_integer()

            self._cpu.pc.write_integer(pc + offset + 4)

    def _handle_immediate(self, imm: int, fmt_token: MIPSToken, statement: MIPSStatement) -> int:
        # rt is not allowed to be zero
        if fmt_token.value == 'rt':
            # TODO: Better error handling
            if imm == 0:
                raise mips_exceptions.ReservedInstructionException()

        return super()._handle_immediate(imm, fmt_token, statement)


@mips32_instruction
class MIPS32BnezalcInstruction(MIPSBaseCompactBranchInstruction):
    def __init__(self, cpu: MIPS32CPU, **kwargs):
        super().__init__(
            'bnezalc',
            'Branch Not Equal To Zero, Compact',
            'bnezalc rt, offset',
            'Compact Branch and link if GPR[rt] is not equal to zero',
            'if GPR[rt] != 0, branch',
            '011000 00000 {rt:05b} {offset:016b}',
            cpu,
            **kwargs
        )

    def execute(self, statement: MIPSStatement) -> None:
        """Do an unconditional PC-relative procedure call."""
        self._execute_prechecks(statement)
        fields = self._get_fields(statement)

        # The condition is evaluated. If the condition is True,
        # the branch is taken.
        rt_address = fields['rt'].value
        rt_value = self._cpu.gpr.read_integer(addr=rt_address, signed=True)
        condition = rt_value != self._cpu.gpr.read_integer(addr=0)

        # Place the return address link in GPR[31]. The return link is the
        # address of the instruction immediately following the branch, where
        # execution continues after a procedure call.
        # The return address link is unconditionally updated.
        self._cpu.gpr.write_integer(
            self._cpu.pc.read_integer() + 4,
            addr=31
        )

        # An 18-bit signed offset (the 16-bit offset field shifted left 2 bits)
        # is added to the address of the instruction following the branch
        # (not the branch itself), to form a PC-relative effective target address.
        if condition:
            offset = fields['offset'] << 2

            pc = self._cpu.pc.read_integer()

            self._cpu.pc.write_integer(pc + offset + 4)

    def _handle_immediate(self, imm: int, fmt_token: MIPSToken, statement: MIPSStatement) -> int:
        # rt is not allowed to be zero
        if fmt_token.value == 'rt':
            # TODO: Better error handling
            if imm == 0:
                raise mips_exceptions.ReservedInstructionException()

        return super()._handle_immediate(imm, fmt_token, statement)


@mips32_instruction
class MIPS32BlezcInstruction(MIPSBaseCompactBranchInstruction):
    def __init__(self, cpu: MIPS32CPU, **kwargs):
        super().__init__(
            'blezc',
            'Branch Less Than or Equal to Zero',
            'blezc rt, offset',
            'Compact Branch if GPR[rt] is less than or equal to zero',
            'if GPR[rt] <= 0, branch',
            '010110 00000 {rt:05b} {offset:016b}',
            cpu,
            **kwargs
        )

    def execute(self, statement: MIPSStatement) -> None:
        """Do an unconditional PC-relative procedure call."""
        self._execute_prechecks(statement)
        fields = self._get_fields(statement)

        # The condition is evaluated. If the condition is True,
        # the branch is taken.
        rt_address = fields['rt'].value
        rt_value = self._cpu.gpr.read_integer(addr=rt_address, signed=True)
        condition = rt_value <= self._cpu.gpr.read_integer(addr=0)

        # An 18-bit signed offset (the 16-bit offset field shifted left 2 bits)
        # is added to the address of the instruction following the branch
        # (not the branch itself), to form a PC-relative effective target address.
        if condition:
            offset = fields['offset'] << 2

            pc = self._cpu.pc.read_integer()

            self._cpu.pc.write_integer(pc + offset + 4)

    def _handle_immediate(self, imm: int, fmt_token: MIPSToken, statement: MIPSStatement) -> int:
        # rt is not allowed to be zero
        if fmt_token.value == 'rt':
            # TODO: Better error handling
            if imm == 0:
                raise mips_exceptions.ReservedInstructionException()

        return super()._handle_immediate(imm, fmt_token, statement)


@mips32_instruction
class MIPS32BgezcInstruction(MIPSBaseCompactBranchInstruction):
    def __init__(self, cpu: MIPS32CPU, **kwargs):
        super().__init__(
            'bgezc',
            'Branch Greater Than or Equal to Zero',
            'bgezc rt, offset',
            'Compact Branch if GPR[rt] is greater than or equal to zero',
            'if GPR[rt] >= 0, branch',
            '010110 {rt:05b} {rt:05b} {offset:016b}',
            cpu,
            **kwargs
        )

    def execute(self, statement: MIPSStatement) -> None:
        """Do an unconditional PC-relative procedure call."""
        self._execute_prechecks(statement)
        fields = self._get_fields(statement)

        # The condition is evaluated. If the condition is True,
        # the branch is taken.
        rt_address = fields['rt'].value
        rt_value = self._cpu.gpr.read_integer(addr=rt_address, signed=True)
        condition = rt_value >= self._cpu.gpr.read_integer(addr=0)

        # An 18-bit signed offset (the 16-bit offset field shifted left 2 bits)
        # is added to the address of the instruction following the branch
        # (not the branch itself), to form a PC-relative effective target address.
        if condition:
            offset = fields['offset'] << 2

            pc = self._cpu.pc.read_integer()

            self._cpu.pc.write_integer(pc + offset + 4)

    def _handle_immediate(self, imm: int, fmt_token: MIPSToken, statement: MIPSStatement) -> int:
        # rt is not allowed to be zero
        if fmt_token.value == 'rt':
            # TODO: Better error handling
            if imm == 0:
                raise mips_exceptions.ReservedInstructionException()

        return super()._handle_immediate(imm, fmt_token, statement)


@mips32_instruction
class MIPS32BgecInstruction(MIPSBaseCompactBranchInstruction):
    def __init__(self, cpu: MIPS32CPU, **kwargs):
        super().__init__(
            'bgec',
            'Branch Greater Than or Equal',
            'bgec rs, rt, offset',
            'Compact Branch if GPR[rs] is greater than or equal to GPR[rt]',
            'if GPR[rs] >= GPR[rt], branch',
            '010110 {rs:05b} {rt:05b} {offset:016b}',
            cpu,
            **kwargs
        )

    def execute(self, statement: MIPSStatement) -> None:
        """Do an unconditional PC-relative procedure call."""
        self._execute_prechecks(statement)
        fields = self._get_fields(statement)

        # The condition is evaluated. If the condition is True,
        # the branch is taken.
        rs_address = fields['rs'].value
        rs_value = self._cpu.gpr.read_integer(addr=rs_address, signed=True)
        rt_address = fields['rt'].value
        rt_value = self._cpu.gpr.read_integer(addr=rt_address, signed=True)

        condition = rs_value >= rt_value

        # An 18-bit signed offset (the 16-bit offset field shifted left 2 bits)
        # is added to the address of the instruction following the branch
        # (not the branch itself), to form a PC-relative effective target address.
        if condition:
            offset = fields['offset'] << 2

            pc = self._cpu.pc.read_integer()

            self._cpu.pc.write_integer(pc + offset + 4)

    def _handle_immediate(self, imm: int, fmt_token: MIPSToken, statement: MIPSStatement) -> int:
        # rt is not allowed to be zero
        if fmt_token.value == 'rs' or fmt_token.value == 'rt':
            # TODO: Better error handling
            if imm == 0:
                raise mips_exceptions.ReservedInstructionException()

        return super()._handle_immediate(imm, fmt_token, statement)

    def _validate_fields(self, fields: typing.Dict[str, int]):
        # rs is not allowed to equal rt
        if fields['rs'] == fields['rt']:
            raise mips_exceptions.ReservedInstructionException()


@mips32_instruction
class MIPS32BgtzcInstruction(MIPSBaseCompactBranchInstruction):
    def __init__(self, cpu: MIPS32CPU, **kwargs):
        super().__init__(
            'bgtzc',
            'Branch Greater Than Zero',
            'bgtzc rt, offset',
            'Compact Branch if GPR[rt] is greater than zero',
            'if GPR[rt] > 0, branch',
            '010111 00000 {rt:05b} {offset:016b}',
            cpu,
            **kwargs
        )

    def execute(self, statement: MIPSStatement) -> None:
        """Do an unconditional PC-relative procedure call."""
        self._execute_prechecks(statement)
        fields = self._get_fields(statement)

        # The condition is evaluated. If the condition is True,
        # the branch is taken.
        rt_address = fields['rt'].value
        rt_value = self._cpu.gpr.read_integer(addr=rt_address, signed=True)
        condition = rt_value > self._cpu.gpr.read_integer(addr=0)

        # An 18-bit signed offset (the 16-bit offset field shifted left 2 bits)
        # is added to the address of the instruction following the branch
        # (not the branch itself), to form a PC-relative effective target address.
        if condition:
            offset = fields['offset'] << 2

            pc = self._cpu.pc.read_integer()

            self._cpu.pc.write_integer(pc + offset + 4)

    def _handle_immediate(self, imm: int, fmt_token: MIPSToken, statement: MIPSStatement) -> int:
        # rt is not allowed to be zero
        if fmt_token.value == 'rt':
            # TODO: Better error handling
            if imm == 0:
                raise mips_exceptions.ReservedInstructionException()

        return super()._handle_immediate(imm, fmt_token, statement)


@mips32_instruction
class MIPS32BltzcInstruction(MIPSBaseCompactBranchInstruction):
    def __init__(self, cpu: MIPS32CPU, **kwargs):
        super().__init__(
            'bltzc',
            'Branch Less Than Zero',
            'bltzc rt, offset',
            'Compact Branch if GPR[rt] is less than zero',
            'if GPR[rt] < 0, branch',
            '010111 {rt:05b} {rt:05b} {offset:016b}',
            cpu,
            **kwargs
        )

    def execute(self, statement: MIPSStatement) -> None:
        """Do an unconditional PC-relative procedure call."""
        self._execute_prechecks(statement)
        fields = self._get_fields(statement)

        # The condition is evaluated. If the condition is True,
        # the branch is taken.
        rt_address = fields['rt'].value
        rt_value = self._cpu.gpr.read_integer(addr=rt_address, signed=True)
        condition = rt_value < self._cpu.gpr.read_integer(addr=0)

        # An 18-bit signed offset (the 16-bit offset field shifted left 2 bits)
        # is added to the address of the instruction following the branch
        # (not the branch itself), to form a PC-relative effective target address.
        if condition:
            offset = fields['offset'] << 2

            pc = self._cpu.pc.read_integer()

            self._cpu.pc.write_integer(pc + offset + 4)

    def _handle_immediate(self, imm: int, fmt_token: MIPSToken, statement: MIPSStatement) -> int:
        # rt is not allowed to be zero
        if fmt_token.value == 'rt':
            # TODO: Better error handling
            if imm == 0:
                raise mips_exceptions.ReservedInstructionException()

        return super()._handle_immediate(imm, fmt_token, statement)


@mips32_instruction
class MIPS32BltcInstruction(MIPSBaseCompactBranchInstruction):
    def __init__(self, cpu: MIPS32CPU, **kwargs):
        super().__init__(
            'bltc',
            'Branch Less Than',
            'bltc rs, rt, offset',
            'Compact Branch if GPR[rs] is less than GPR[rt]',
            'if GPR[rs] < GPR[rt], branch',
            '010111 {rs:05b} {rt:05b} {offset:016b}',
            cpu,
            **kwargs
        )

    def execute(self, statement: MIPSStatement) -> None:
        """Do an unconditional PC-relative procedure call."""
        self._execute_prechecks(statement)
        fields = self._get_fields(statement)

        # The condition is evaluated. If the condition is True,
        # the branch is taken.
        rs_address = fields['rs'].value
        rs_value = self._cpu.gpr.read_integer(addr=rs_address, signed=True)
        rt_address = fields['rt'].value
        rt_value = self._cpu.gpr.read_integer(addr=rt_address, signed=True)

        condition = rs_value < rt_value

        # An 18-bit signed offset (the 16-bit offset field shifted left 2 bits)
        # is added to the address of the instruction following the branch
        # (not the branch itself), to form a PC-relative effective target address.
        if condition:
            offset = fields['offset'] << 2

            pc = self._cpu.pc.read_integer()

            self._cpu.pc.write_integer(pc + offset + 4)

    def _handle_immediate(self, imm: int, fmt_token: MIPSToken, statement: MIPSStatement) -> int:
        # rt is not allowed to be zero
        if fmt_token.value == 'rs' or fmt_token.value == 'rt':
            # TODO: Better error handling
            if imm == 0:
                raise mips_exceptions.ReservedInstructionException()

        return super()._handle_immediate(imm, fmt_token, statement)

    def _validate_fields(self, fields: typing.Dict[str, int]):
        # rs must not equal rt
        if fields['rs'] == fields['rt']:
            # TODO: Better error handling
            raise mips_exceptions.ReservedInstructionException()


@mips32_instruction
class MIPS32BgeucInstruction(MIPSBaseCompactBranchInstruction):
    def __init__(self, cpu: MIPS32CPU, **kwargs):
        super().__init__(
            'bgeuc',
            'Branch Greater Than or Equal Unsigned',
            'bgeuc rs, rt, offset',
            'Compact Branch if GPR[rs] is greater than or equal to GPR[rt] (unsigned)',
            'if GPR[rs] >= GPR[rt], branch',
            '000110 {rs:05b} {rt:05b} {offset:016b}',
            cpu,
            **kwargs
        )

    def execute(self, statement: MIPSStatement) -> None:
        """Do an unconditional PC-relative procedure call."""
        self._execute_prechecks(statement)
        fields = self._get_fields(statement)

        # The condition is evaluated. If the condition is True,
        # the branch is taken.
        rs_address = fields['rs'].value
        rs_value = self._cpu.gpr.read_integer(addr=rs_address, signed=False)
        rt_address = fields['rt'].value
        rt_value = self._cpu.gpr.read_integer(addr=rt_address, signed=False)

        condition = rs_value >= rt_value

        # An 18-bit signed offset (the 16-bit offset field shifted left 2 bits)
        # is added to the address of the instruction following the branch
        # (not the branch itself), to form a PC-relative effective target address.
        if condition:
            offset = fields['offset'] << 2

            pc = self._cpu.pc.read_integer()

            self._cpu.pc.write_integer(pc + offset + 4)

    def _handle_immediate(self, imm: int, fmt_token: MIPSToken, statement: MIPSStatement) -> int:
        # rt is not allowed to be zero
        if fmt_token.value == 'rs' or fmt_token == 'rt':
            # TODO: Better error handling
            if imm == 0:
                raise mips_exceptions.ReservedInstructionException()

        return super()._handle_immediate(imm, fmt_token, statement)

    def _validate_fields(self, fields: typing.Dict[str, int]):
        # rs must not equal rt
        if fields['rs'] == fields['rt']:
            # TODO: Better error handling
            raise mips_exceptions.ReservedInstructionException()


@mips32_instruction
class MIPS32BltucInstruction(MIPSBaseCompactBranchInstruction):
    def __init__(self, cpu: MIPS32CPU, **kwargs):
        super().__init__(
            'bltuc',
            'Branch Less Than Unsigned',
            'bltuc rs, rt, offset',
            'Compact Branch if GPR[rs] is less than GPR[rt] (unsigned)',
            'if GPR[rs] < GPR[rt], branch',
            '000111 {rs:05b} {rt:05b} {offset:016b}',
            cpu,
            **kwargs
        )

    def execute(self, statement: MIPSStatement) -> None:
        """Do an unconditional PC-relative procedure call."""
        self._execute_prechecks(statement)
        fields = self._get_fields(statement)

        # The condition is evaluated. If the condition is True,
        # the branch is taken.
        rs_address = fields['rs'].value
        rs_value = self._cpu.gpr.read_integer(addr=rs_address, signed=False)
        rt_address = fields['rt'].value
        rt_value = self._cpu.gpr.read_integer(addr=rt_address, signed=False)

        condition = rs_value < rt_value

        # An 18-bit signed offset (the 16-bit offset field shifted left 2 bits)
        # is added to the address of the instruction following the branch
        # (not the branch itself), to form a PC-relative effective target address.
        if condition:
            offset = fields['offset'] << 2

            pc = self._cpu.pc.read_integer()

            self._cpu.pc.write_integer(pc + offset + 4)

    def _handle_immediate(self, imm: int, fmt_token: MIPSToken, statement: MIPSStatement) -> int:
        # rt is not allowed to be zero
        if fmt_token.value == 'rs' or fmt_token == 'rt':
            # TODO: Better error handling
            if imm == 0:
                raise mips_exceptions.ReservedInstructionException()

        return super()._handle_immediate(imm, fmt_token, statement)

    def _validate_fields(self, fields: typing.Dict[str, int]):
        # rs must not equal rt
        if fields['rs'] == fields['rt']:
            # TODO: Better error handling
            raise mips_exceptions.ReservedInstructionException()


@mips32_instruction
class MIPS32BeqcInstruction(MIPSBaseCompactBranchInstruction):
    def __init__(self, cpu: MIPS32CPU, **kwargs):
        super().__init__(
            'beqc',
            'Branch Equal',
            'beqc rs, rt, offset',
            'Compact Branch if GPR[rs] is equal to GPR[rt]',
            'if GPR[rs] == GPR[rt], branch',
            '001000 {rs:05b} {rt:05b} {offset:016b}',
            cpu,
            **kwargs
        )

    def execute(self, statement: MIPSStatement) -> None:
        """Do an unconditional PC-relative procedure call."""
        self._execute_prechecks(statement)
        fields = self._get_fields(statement)

        # The condition is evaluated. If the condition is True,
        # the branch is taken.
        rs_address = fields['rs'].value
        rs_value = self._cpu.gpr.read_integer(addr=rs_address)
        rt_address = fields['rt'].value
        rt_value = self._cpu.gpr.read_integer(addr=rt_address)

        condition = rs_value == rt_value

        # An 18-bit signed offset (the 16-bit offset field shifted left 2 bits)
        # is added to the address of the instruction following the branch
        # (not the branch itself), to form a PC-relative effective target address.
        if condition:
            offset = fields['offset'] << 2

            pc = self._cpu.pc.read_integer()

            self._cpu.pc.write_integer(pc + offset + 4)

    def _handle_immediate(self, imm: int, fmt_token: MIPSToken, statement: MIPSStatement) -> int:
        # rt is not allowed to be zero
        if fmt_token.value == 'rs' or fmt_token == 'rt':
            # TODO: Better error handling
            if imm == 0:
                raise mips_exceptions.ReservedInstructionException()

        return super()._handle_immediate(imm, fmt_token, statement)

    def _validate_fields(self, fields: typing.Dict[str, int]):
        # rs must be less than rt
        if fields['rs'] >= fields['rt']:
            # TODO: Better error handling
            raise mips_exceptions.ReservedInstructionException()


@mips32_instruction
class MIPS32BnecInstruction(MIPSBaseCompactBranchInstruction):
    def __init__(self, cpu: MIPS32CPU, **kwargs):
        super().__init__(
            'bnec',
            'Branch Not Equal',
            'bnec rs, rt, offset',
            'Compact Branch if GPR[rs] is not equal to GPR[rt]',
            'if GPR[rs] != GPR[rt], branch',
            '011000 {rs:05b} {rt:05b} {offset:016b}',
            cpu,
            **kwargs
        )

    def execute(self, statement: MIPSStatement) -> None:
        """Do an unconditional PC-relative procedure call."""
        self._execute_prechecks(statement)
        fields = self._get_fields(statement)

        # The condition is evaluated. If the condition is True,
        # the branch is taken.
        rs_address = fields['rs'].value
        rs_value = self._cpu.gpr.read_integer(addr=rs_address)
        rt_address = fields['rt'].value
        rt_value = self._cpu.gpr.read_integer(addr=rt_address)

        condition = rs_value != rt_value

        # An 18-bit signed offset (the 16-bit offset field shifted left 2 bits)
        # is added to the address of the instruction following the branch
        # (not the branch itself), to form a PC-relative effective target address.
        if condition:
            offset = fields['offset'] << 2

            pc = self._cpu.pc.read_integer()

            self._cpu.pc.write_integer(pc + offset + 4)

    def _handle_immediate(self, imm: int, fmt_token: MIPSToken, statement: MIPSStatement) -> int:
        # rt is not allowed to be zero
        if fmt_token.value == 'rs' or fmt_token == 'rt':
            # TODO: Better error handling
            if imm == 0:
                raise mips_exceptions.ReservedInstructionException()

        return super()._handle_immediate(imm, fmt_token, statement)

    def _validate_fields(self, fields: typing.Dict[str, int]):
        # rs must be less than rt
        if fields['rs'] >= fields['rt']:
            # TODO: Better error handling
            raise mips_exceptions.ReservedInstructionException()


@mips32_instruction
class MIPS32BeqzcInstruction(MIPSBaseCompactBranchInstruction):
    def __init__(self, cpu: MIPS32CPU, **kwargs):
        super().__init__(
            'beqzc',
            'Branch Equal to Zero',
            'beqzc rs, offset',
            'Compact Branch if GPR[rs] is equal to zero',
            'if GPR[rs] == 0, branch',
            '110110 {rs:05b} {offset:021b}',
            cpu,
            **kwargs
        )

    def execute(self, statement: MIPSStatement) -> None:
        """Do an unconditional PC-relative procedure call."""
        self._execute_prechecks(statement)
        fields = self._get_fields(statement)

        # The condition is evaluated. If the condition is True,
        # the branch is taken.
        rs_address = fields['rs'].value
        rs_value = self._cpu.gpr.read_integer(addr=rs_address)

        condition = rs_value == self._cpu.gpr.read_integer(addr=0)

        # An 23-bit signed offset (the 21-bit offset field shifted left 2 bits)
        # is added to the address of the instruction following the branch
        # (not the branch itself), to form a PC-relative effective target address.
        if condition:
            offset = fields['offset'] << 2

            pc = self._cpu.pc.read_integer()

            self._cpu.pc.write_integer(pc + offset + 4)

    def _handle_immediate(self, imm: int, fmt_token: MIPSToken, statement: MIPSStatement) -> int:
        # rt is not allowed to be zero
        if fmt_token.value == 'rs':
            # TODO: Better error handling
            if imm == 0:
                raise mips_exceptions.ReservedInstructionException()

        return super()._handle_immediate(imm, fmt_token, statement)


@mips32_instruction
class MIPS32BnezcInstruction(MIPSBaseCompactBranchInstruction):
    def __init__(self, cpu: MIPS32CPU, **kwargs):
        super().__init__(
            'bnezc',
            'Branch Not Equal to Zero',
            'bnezc rs, offset',
            'Compact Branch if GPR[rs] is not equal to zero',
            'if GPR[rs] != 0, branch',
            '111110 {rs:05b} {offset:021b}',
            cpu,
            **kwargs
        )

    def execute(self, statement: MIPSStatement) -> None:
        """Do an unconditional PC-relative procedure call."""
        self._execute_prechecks(statement)
        fields = self._get_fields(statement)

        # The condition is evaluated. If the condition is True,
        # the branch is taken.
        rs_address = fields['rs'].value
        rs_value = self._cpu.gpr.read_integer(addr=rs_address)

        condition = rs_value != self._cpu.gpr.read_integer(addr=0)

        # An 23-bit signed offset (the 21-bit offset field shifted left 2 bits)
        # is added to the address of the instruction following the branch
        # (not the branch itself), to form a PC-relative effective target address.
        if condition:
            offset = fields['offset'] << 2

            pc = self._cpu.pc.read_integer()

            self._cpu.pc.write_integer(pc + offset + 4)

    def _handle_immediate(self, imm: int, fmt_token: MIPSToken, statement: MIPSStatement) -> int:
        # rt is not allowed to be zero
        if fmt_token.value == 'rs':
            # TODO: Better error handling
            if imm == 0:
                raise mips_exceptions.ReservedInstructionException()

        return super()._handle_immediate(imm, fmt_token, statement)


@mips32_instruction
class MIPS32BgtzInstruction(MIPSBaseBranchInstruction):
    def __init__(self, cpu: MIPS32CPU, **kwargs):
        super().__init__(
            'bgtz',
            'Branch on Greater Than Zero',
            'bgtz rs, offset',
            'Branch if GPR[rs] is greater than zero',
            'if GPR[rs] > 0 then branch',
            '000101 {rs:05b} 00000 {offset:016b}',
            cpu,
            **kwargs
        )

    def execute(self, statement: MIPSStatement) -> None:
        """Compare GPRs then do a PC-relative conditional branch."""
        self._execute_prechecks(statement)
        fields = self._get_fields(statement)

        # An 18-bit signed offset (the 16-bit offset field shifted left 2-bits)
        # is added to the address of the instruction following the branch (not
        # the branch itself), in the branch delay slot, to form a PC-relative
        # target address.
        offset = numeric.to_int(fields['offset'].value << 2, size=constants.MIPSMemorySize.WORD)

        rs_address = fields['rs'].value
        rs_value = self._cpu.gpr.read_integer(addr=rs_address, signed=True)

        # If the contents of GPR[rs] are greater than zero, branch to
        # the effective target address after the instruction in the delay slot
        # is executed.
        self._execute_delay_slot(statement)

        if rs_value > self._cpu.gpr.read_integer(addr=0):
            pc = self._cpu.pc.read_integer()
            self._cpu.pc.write_integer(pc + offset)


@mips32_instruction
class MIPS32BitswapInstruction(MIPSBaseBranchInstruction):
    def __init__(self, cpu: MIPS32CPU, **kwargs):
        super().__init__(
            'bitswap',
            'Swap Bits',
            'bitswap rd, rt',
            'Reverse bits in each byte',
            'GPR[rd].byte[i] = reversed(GPR[rt].byte(i)) for i in NUM_BYTES',
            '011111 00000 {rt:05b} {rd:05b} 00000 100000',
            cpu,
            **kwargs
        )

    def execute(self, statement: MIPSStatement) -> None:
        """Reverse bits in each byte."""
        self._execute_prechecks(statement)
        fields = self._get_fields(statement)

        # Each byte in GPR[rt] is moved to the same byte position in output
        # GPR[rd], with bits in each byte reversed.
        rd_address = fields['rd'].value

        rt_address = fields['rt'].value
        rt_value = self._cpu.gpr.read_integer(addr=rt_address)

        rt_value_bytes = numeric.to_bytes(rt_value, constants.MIPSMemorySize.WORD_LENGTH_BYTES)
        res_bytes = []
        for in_byte in rt_value_bytes:
            tmp = 0
            for i in range(constants.MIPSMemorySize.BYTE):
                if numeric.get_bit(in_byte, i):
                    tmp |= numeric.set_bit(tmp, i)

            res_bytes.append(tmp)

        res = numeric.from_bytes(res_bytes, constants.MIPSMemorySize.WORD)
        self._cpu.gpr.write_integer(res, addr=rd_address)


@mips32_instruction
class MIPS32BlezInstruction(MIPSBaseBranchInstruction):
    def __init__(self, cpu: MIPS32CPU, **kwargs):
        super().__init__(
            'blez',
            'Branch on Less Than or Equal to Zero',
            'blez rs, offset',
            'Branch if GPR[rs] is less than or equal to zero',
            'if GPR[rs] <= 0 then branch',
            '000110 {rs:05b} 00000 {offset:016b}',
            cpu,
            **kwargs
        )

    def execute(self, statement: MIPSStatement) -> None:
        """Compare GPRs then do a PC-relative conditional branch."""
        self._execute_prechecks(statement)
        fields = self._get_fields(statement)

        # An 18-bit signed offset (the 16-bit offset field shifted left 2-bits)
        # is added to the address of the instruction following the branch (not
        # the branch itself), in the branch delay slot, to form a PC-relative
        # target address.
        offset = numeric.to_int(fields['offset'].value << 2, size=constants.MIPSMemorySize.WORD)

        rs_address = fields['rs'].value
        rs_value = self._cpu.gpr.read_integer(addr=rs_address, signed=True)

        # If the contents of GPR[rs] are less than or equal to zero, branch to
        # the effective target address after the instruction in the delay slot
        # is executed.
        self._execute_delay_slot(statement)

        if rs_value <= self._cpu.gpr.read_integer(addr=0):
            pc = self._cpu.pc.read_integer()
            self._cpu.pc.write_integer(pc + offset)


@mips32_instruction
class MIPS32BltzInstruction(MIPSBaseBranchInstruction):
    def __init__(self, cpu: MIPS32CPU, **kwargs):
        super().__init__(
            'bltz',
            'Branch on Less Than Zero',
            'bltz rs, offset',
            'Branch if GPR[rs] is less than zero',
            'if GPR[rs] < 0 then branch',
            '000001 {rs:05b} 00000 {offset:016b}',
            cpu,
            **kwargs
        )

    def execute(self, statement: MIPSStatement) -> None:
        """Compare GPRs then do a PC-relative conditional branch."""
        self._execute_prechecks(statement)
        fields = self._get_fields(statement)

        # An 18-bit signed offset (the 16-bit offset field shifted left 2-bits)
        # is added to the address of the instruction following the branch (not
        # the branch itself), in the branch delay slot, to form a PC-relative
        # target address.
        offset = numeric.to_int(fields['offset'].value << 2, size=constants.MIPSMemorySize.WORD)

        rs_address = fields['rs'].value
        rs_value = self._cpu.gpr.read_integer(addr=rs_address, signed=True)

        # If the contents of GPR[rs] are less than or equal to zero, branch to
        # the effective target address after the instruction in the delay slot
        # is executed.
        self._execute_delay_slot(statement)

        if rs_value < self._cpu.gpr.read_integer(addr=0):
            pc = self._cpu.pc.read_integer()
            self._cpu.pc.write_integer(pc + offset)


@mips32_instruction
class MIPS32BneInstruction(MIPSBaseBranchInstruction):
    def __init__(self, cpu: MIPS32CPU, **kwargs):
        super().__init__(
            'bne',
            'Branch on Not Equal',
            'bne rs, rt, offset',
            'Branch if contents of registers are not equal',
            'if GPR[rs] != GPR[rt] then branch',
            '000101 {rs:05b} {rt:05b} {offset:016b}',
            cpu,
            **kwargs
        )

    def execute(self, statement: MIPSStatement) -> None:
        """Compare GPRs then do a PC-relative conditional branch."""
        self._execute_prechecks(statement)
        fields = self._get_fields(statement)

        # An 18-bit signed offset (the 16-bit offset field shifted left 2-bits)
        # is added to the address of the instruction following the branch (not
        # the branch itself), in the branch delay slot, to form a PC-relative
        # target address.
        offset = numeric.to_int(fields['offset'].value << 2, size=constants.MIPSMemorySize.WORD)

        rs_address = fields['rs'].value
        rs_value = self._cpu.gpr.read_integer(addr=rs_address)

        rt_address = fields['rt'].value
        rt_value = self._cpu.gpr.read_integer(addr=rt_address)

        # If the contents of GPR[rs] and GPR[rt] are not equal, branch to
        # the effective target address after the instruction in the delay slot
        # is executed.
        self._execute_delay_slot(statement)

        if rs_value != rt_value:
            pc = self._cpu.pc.read_integer()
            self._cpu.pc.write_integer(pc + offset)


@mips32_instruction
class MIPS32BovcInstruction(MIPSBaseBranchInstruction):
    def __init__(self, cpu: MIPS32CPU, **kwargs):
        super().__init__(
            'bovc',
            'Branch on Overflow',
            'bovc rs, rt, offset',
            'Branch if signed 32-bit addition causes an overflow',
            'if GPR[rs] + GPR[rt] overflows, branch',
            '001000 {rs:05b} {rt:05b} {offset:016b}',
            cpu,
            **kwargs
        )

    def execute(self, statement: MIPSStatement) -> None:
        """Compare GPRs then do a PC-relative conditional branch."""
        self._execute_prechecks(statement)
        fields = self._get_fields(statement)

        # Perform a signed 32-bit addition of GPR[rs] and GPR[rt]. Discard the sum.
        rs_address = fields['rs'].value
        rs_value = self._cpu.gpr.read_integer(addr=rs_address)

        rt_address = fields['rt'].value
        rt_value = self._cpu.gpr.read_integer(addr=rt_address)

        res = rs_value + rt_value

        # Branch if overflow is detected
        if numeric.detect_overflow(rs_value, rt_value, res):
            # An 18-bit signed offset (the 16-bit offset field shifted left 2 bits)
            # is added to the address of the instruction following the branch
            # (not the branch itself), to form a PC-relative effective target address.
            offset = fields['offset'] << 2
            pc = self._cpu.pc.read_integer()
            self._cpu.pc.write_integer(pc + offset + 4)


@mips32_instruction
class MIPS32BovcInstruction(MIPSBaseBranchInstruction):
    def __init__(self, cpu: MIPS32CPU, **kwargs):
        super().__init__(
            'bnvc',
            'Branch on no Overflow',
            'bnvc rs, rt, offset',
            'Branch if signed 32-bit addition does not cause an overflow',
            'if GPR[rs] + GPR[rt] does not overflow, branch',
            '011000 {rs:05b} {rt:05b} {offset:016b}',
            cpu,
            **kwargs
        )

    def execute(self, statement: MIPSStatement) -> None:
        """Compare GPRs then do a PC-relative conditional branch."""
        self._execute_prechecks(statement)
        fields = self._get_fields(statement)

        # Perform a signed 32-bit addition of GPR[rs] and GPR[rt]. Discard the sum.
        rs_address = fields['rs'].value
        rs_value = self._cpu.gpr.read_integer(addr=rs_address)

        rt_address = fields['rt'].value
        rt_value = self._cpu.gpr.read_integer(addr=rt_address)

        res = rs_value + rt_value

        # Branch if overflow is detected
        if not numeric.detect_overflow(rs_value, rt_value, res):
            # An 18-bit signed offset (the 16-bit offset field shifted left 2 bits)
            # is added to the address of the instruction following the branch
            # (not the branch itself), to form a PC-relative effective target address.
            offset = fields['offset'] << 2
            pc = self._cpu.pc.read_integer()
            self._cpu.pc.write_integer(pc + offset + 4)


@mips32_instruction
class MIPS32BreakInstruction(MIPSBaseBranchInstruction):
    def __init__(self, cpu: MIPS32CPU, **kwargs):
        super().__init__(
            'break',
            'Breakpoint',
            'break',
            'Cause a BREAKPOINT exception',
            'raise Breakpoint',
            '000000 00000000000000000000 001101',
            cpu,
            **kwargs
        )

    def execute(self, statement: MIPSStatement) -> None:
        """Cause a BREAKPOINT exception."""
        self._execute_prechecks(statement)

        raise mips_exceptions.BreakException()


@mips32_instruction
class MIPS32CloInstruction(MIPSBasicInstruction):
    def __init__(self, cpu: MIPS32CPU, **kwargs):
        super().__init__(
            'clo',
            'Count Leading Ones',
            'clo rd, rs',
            'Count the number of leading ones in a word.',
            'GPR[rd] = count_leading_ones(GPR[rs])',
            '000000 {rs:05b} 00000 {rd:05b} 00001 010001',
            cpu,
            **kwargs
        )

    def execute(self, statement: MIPSStatement) -> None:
        """Count Leading Ones."""
        self._execute_prechecks(statement)
        fields = self._get_fields(statement)

        # Bits 31..0 of GPR[rs] are scanned from most significant to least
        # significant bit. The number of leading ones is counted and the
        # result is written to GPR[rd].
        rs_address = fields['rs'].value
        rs_value = self._cpu.gpr.read_integer(addr=rs_address)

        cnt = 0
        for i in reversed(range(32)):
            if not numeric.get_bit(rs_value, i):
                break

            cnt += 1

        rd_address = fields['rd'].value
        self._cpu.gpr.write_integer(cnt, addr=rd_address)


@mips32_instruction
class MIPS32ClzInstruction(MIPSBasicInstruction):
    def __init__(self, cpu: MIPS32CPU, **kwargs):
        super().__init__(
            'clz',
            'Count Leading Zeroes',
            'clz rd, rs',
            'Count the number of leading zeroes in a word.',
            'GPR[rd] = count_leading_zeroes(GPR[rs])',
            '000000 {rs:05b} 00000 {rd:05b} 00001 010000',
            cpu,
            **kwargs
        )

    def execute(self, statement: MIPSStatement) -> None:
        """Count Leading Zeroes."""
        self._execute_prechecks(statement)
        fields = self._get_fields(statement)

        # Bits 31..0 of GPR[rs] are scanned from most significant to least
        # significant bit. The number of leading zeroes is counted and the
        # result is written to GPR[rd].
        rs_address = fields['rs'].value
        rs_value = self._cpu.gpr.read_integer(addr=rs_address)

        cnt = 0
        for i in reversed(range(32)):
            if numeric.get_bit(rs_value, i):
                break

            cnt += 1

        rd_address = fields['rd'].value
        self._cpu.gpr.write_integer(cnt, addr=rd_address)


@mips32_instruction
class MIPS32DiInstruction(MIPSBasicInstruction):
    def __init__(self, cpu: MIPS32CPU, **kwargs):
        super().__init__(
            'di',
            'Disable Interrupts',
            'di rt',
            'Return the previous value of STATUS and disable interrupts',
            'GPR[rt] = STATUS',
            '010000 01011 {rt:05b} 01100 00000 0 00 000',
            cpu,
            **kwargs
        )

    def execute(self, statement: MIPSStatement) -> None:
        """Disable Interrupts"""
        self._execute_prechecks(statement)
        fields = self._get_fields(statement)

        # TODO: Implement
        raise mips_exceptions.CoprocessorUnusableException


@mips32_instruction
class MIPS32DivInstruction(MIPSBasicInstruction):
    def __init__(self, cpu: MIPS32CPU, **kwargs):
        super().__init__(
            'div',
            'Signed Integer Division',
            'div rd, rs, rt',
            'Perform signed integer division',
            'GPR[rd] = GPR[rs] / GPR[rt]',
            '000000 {rs:05b} {rt:05b} {rd:05b} 00010 011010',
            cpu,
            **kwargs
        )

    def execute(self, statement: MIPSStatement) -> None:
        """Signed integer division"""
        self._execute_prechecks(statement)
        fields = self._get_fields(statement)

        # DIV performs a signed 32-bit integer division,
        # and places the 32-bit quotient result in GPR[rd].
        rd_address = fields['rd'].value

        rs_address = fields['rs'].value
        rs_value = self._cpu.gpr.read_integer(addr=rs_address, signed=True)

        rt_address = fields['rt'].value
        rt_value = self._cpu.gpr.read_integer(addr=rt_address, signed=True)

        try:
            res = rs_value // rt_value
        except ZeroDivisionError:
            raise mips_exceptions.DivideByZeroException()

        self._cpu.gpr.write_integer(res, addr=rd_address)


@mips32_instruction
class MIPS32DivuInstruction(MIPSBasicInstruction):
    def __init__(self, cpu: MIPS32CPU, **kwargs):
        super().__init__(
            'divu',
            'Unsigned Integer Division',
            'divu rd, rs, rt',
            'Perform unsigned integer division',
            'GPR[rd] = GPR[rs] / GPR[rt]',
            '000000 {rs:05b} {rt:05b} {rd:05b} 00010 011011',
            cpu,
            **kwargs
        )

    def execute(self, statement: MIPSStatement) -> None:
        """Unsigned integer division"""
        self._execute_prechecks(statement)
        fields = self._get_fields(statement)

        # DIV performs a signed 32-bit integer division,
        # and places the 32-bit quotient result in GPR[rd].
        rd_address = fields['rd'].value

        rs_address = fields['rs'].value
        rs_value = self._cpu.gpr.read_integer(addr=rs_address, signed=False)

        rt_address = fields['rt'].value
        rt_value = self._cpu.gpr.read_integer(addr=rt_address, signed=False)

        try:
            res = rs_value // rt_value
        except ZeroDivisionError:
            raise mips_exceptions.DivideByZeroException()

        self._cpu.gpr.write_integer(res, addr=rd_address)


@mips32_instruction
class MIPS32EiInstruction(MIPSBasicInstruction):
    def __init__(self, cpu: MIPS32CPU, **kwargs):
        super().__init__(
            'ei',
            'Enable Interrupts',
            'ei rt',
            'Return the previous value of STATUS and enable interrupts',
            'GPR[rt] = STATUS',
            '010000 01011 {rt:05b} 01100 00000 1 00 000',
            cpu,
            **kwargs
        )

    def execute(self, statement: MIPSStatement) -> None:
        """Enable Interrupts"""
        self._execute_prechecks(statement)
        fields = self._get_fields(statement)

        # TODO: Implement
        raise mips_exceptions.CoprocessorUnusableException


@mips32_instruction
class MIPS32EretInstruction(MIPSBasicInstruction):
    def __init__(self, cpu: MIPS32CPU, **kwargs):
        super().__init__(
            'eret',
            'Exception Return',
            'eret',
            'Return from interrupt, exception or error trap',
            '',
            '010000 1 0000000000000000000 011000',
            cpu,
            **kwargs
        )

    def execute(self, statement: MIPSStatement) -> None:
        """Exception Return"""
        self._execute_prechecks(statement)
        fields = self._get_fields(statement)

        # TODO: Implement
        raise mips_exceptions.CoprocessorUnusableException


@mips32_instruction
class MIPS32EretncInstruction(MIPSBasicInstruction):
    def __init__(self, cpu: MIPS32CPU, **kwargs):
        super().__init__(
            'eretnc',
            'Exception Return No Clear',
            'eretnc',
            'Return from interrupt, exception or error trap without clearing LL bit',
            '',
            '010000 1 000000000000000000 1 011000',
            cpu,
            **kwargs
        )

    def execute(self, statement: MIPSStatement) -> None:
        """Exception Return No Clear"""
        self._execute_prechecks(statement)
        fields = self._get_fields(statement)

        # TODO: Implement
        raise mips_exceptions.CoprocessorUnusableException


@mips32_instruction
class MIPS32ExtInstruction(MIPSBasicInstruction):
    def __init__(self, cpu: MIPS32CPU, **kwargs):
        super().__init__(
            'ext',
            'Extract Bit Field',
            'ext rt, rs, pos, size',
            'Extract a bit field from GPR[rs] and store it right-justified in GPR[rt]',
            'GPR[rt] = extract_field(GPR[rs], size-1, pos)',
            '011111 {rs:05b} {rt:05b} {size:05b} {pos:05b} 000000',
            cpu,
            **kwargs
        )

    def execute(self, statement: MIPSStatement) -> None:
        """Exception Return"""
        self._execute_prechecks(statement)
        fields = self._get_fields(statement)

        # The bit field starting at bit pos and extending
        # for size bits is extracted from GPR[rs]...
        pos = fields['pos'].value
        size = fields['size'].value
        rs_address = fields['rs'].value
        rs_value = self._cpu.gpr.read_integer(addr=rs_address)

        res = numeric.get_bits(rs_value, pos, pos + size)

        # ... and stored zero-extended and right-justified in GPR[rt].
        rt_address = fields['rt'].value
        self._cpu.gpr.write_integer(res, addr=rt_address)

    def _validate_fields(self, fields: typing.Dict[str, int]):
        if not (0 < fields['pos'] + fields['size'] <= constants.MIPSMemorySize.WORD):
            raise mips_exceptions.ReservedInstructionException()

        super()._validate_fields(fields)

    def _handle_immediate(self, imm: int, fmt_token: MIPSToken, statement: MIPSStatement) -> int:
        if fmt_token.value == 'pos':
            if not (0 <= imm <= constants.MIPSMemorySize.WORD):
                raise mips_exceptions.ReservedInstructionException()

        if fmt_token.value == 'size':
            if not (0 < imm <= constants.MIPSMemorySize.WORD):
                raise mips_exceptions.ReservedInstructionException()
            return imm - 1

        return super()._handle_immediate(imm, fmt_token, statement)


@mips32_instruction
class MIPS32InsInstruction(MIPSBasicInstruction):
    def __init__(self, cpu: MIPS32CPU, **kwargs):
        super().__init__(
            'ins',
            'Insert Bit Field',
            'ins rt, rs, pos, size',
            'Insert a bit field from GPR[rs] in GPR[rt]',
            'GPR[rt] = extract_field(GPR[rs], size-1, pos)',
            '011111 {rs:05b} {rt:05b} {size:05b} {pos:05b} 000000',
            cpu,
            **kwargs
        )

    def execute(self, statement: MIPSStatement) -> None:
        """Exception Return"""
        self._execute_prechecks(statement)
        fields = self._get_fields(statement)

        # TODO: Implement
        raise mips_exceptions.ReservedInstructionException()

        # The right-most size bits from GPR[rs] are merged into the value in
        # GPR[rt] starting at bit position pos.
        pos = fields['pos'].value
        size = fields['size'].value

        rs_address = fields['rs'].value
        rs_value = self._cpu.gpr.read_integer(addr=rs_address)

        rt_address = fields['rt'].value
        rt_value = self._cpu.gpr.read_integer(addr=rt_address)

        tmp = numeric.get_bits(rs_value, 0, size)
        res = rt_value | tmp

        # The result is placed back in GPR[rt].
        rt_address = fields['rt'].value
        self._cpu.gpr.write_integer(res, addr=rt_address)

    def _validate_fields(self, fields: typing.Dict[str, int]):
        if not (0 < fields['pos'] + fields['size'] <= constants.MIPSMemorySize.WORD):
            raise mips_exceptions.ReservedInstructionException()

        super()._validate_fields(fields)

    def _handle_immediate(self, imm: int, fmt_token: MIPSToken, statement: MIPSStatement) -> int:
        if fmt_token.value == 'pos':
            if not (0 <= imm <= constants.MIPSMemorySize.WORD):
                raise mips_exceptions.ReservedInstructionException()

        if fmt_token.value == 'size':
            if not (0 < imm <= constants.MIPSMemorySize.WORD):
                raise mips_exceptions.ReservedInstructionException()
            return imm - 1

        return super()._handle_immediate(imm, fmt_token, statement)


@mips_deprecated(MIPS32BalcInstruction)
@mips32_instruction
class MIPS32JalInstruction(MIPSBaseJumpInstruction):
    def __init__(self, cpu: MIPS32CPU, **kwargs):
        super().__init__(
            'jal',
            'Jump and Link',
            'jal target',
            'Jump and link to target',
            'GPR[$ra] = PC + 8; PC = target',
            '000011 {target:026b}',
            cpu,
            **kwargs
        )

    def execute(self, statement: MIPSStatement) -> None:
        """Execute a procedure call within the current 256MB-aligned region."""
        self._execute_prechecks(statement)
        fields = self._get_fields(statement)

        # Place the return address link in GPR[31]. The return link is the
        # address of the second instruction following the branch, at which
        # location execution continues after a procedure call.
        if self._cpu.do_delay_slots:
            return_address = self._cpu.pc.read_integer() + 8

        else:
            return_address = self._cpu.pc.read_integer() + 4

        self._cpu.gpr.write_integer(return_address, addr=31)

        # The low 28-bits of the target address is the target field shifted
        # left 2 bits. The remaining upper bits are the corresponding bits of
        # the address of the instruction in the delay slot (not the branch itself).
        target = fields['target'].value << 2
        pc_mask = 0xf0000000
        target = target | (self._cpu.pc.read_integer() & pc_mask)

        self._execute_delay_slot(statement)

        # Adjust for the PC incrementing after each instruction
        self._cpu.pc.write_integer(target - 4)


@mips32_instruction
class MIPS32ModInstruction(MIPSBasicInstruction):
    def __init__(self, cpu: MIPS32CPU, **kwargs):
        super().__init__(
            'mod',
            'Signed Integer Modulo',
            'mod rd, rs, rt',
            'Perform signed integer modulo',
            'GPR[rd] = GPR[rs] % GPR[rt]',
            '000000 {rs:05b} {rt:05b} {rd:05b} 00011 011010',
            cpu,
            **kwargs
        )

    def execute(self, statement: MIPSStatement) -> None:
        """Signed integer modulo"""
        self._execute_prechecks(statement)
        fields = self._get_fields(statement)

        # MOD performs a signed 32-bit integer modulo,
        # and places the 32-bit quotient result in GPR[rd].
        rd_address = fields['rd'].value

        rs_address = fields['rs'].value
        rs_value = self._cpu.gpr.read_integer(addr=rs_address, signed=True)

        rt_address = fields['rt'].value
        rt_value = self._cpu.gpr.read_integer(addr=rt_address, signed=True)

        try:
            res = rs_value % rt_value
        except ZeroDivisionError:
            raise mips_exceptions.DivideByZeroException()

        self._cpu.gpr.write_integer(res, addr=rd_address)


@mips32_instruction
class MIPS32ModuInstruction(MIPSBasicInstruction):
    def __init__(self, cpu: MIPS32CPU, **kwargs):
        super().__init__(
            'modu',
            'Unsigned Integer Modulo',
            'modu rd, rs, rt',
            'Perform unsigned integer modulo',
            'GPR[rd] = GPR[rs] % GPR[rt]',
            '000000 {rs:05b} {rt:05b} {rd:05b} 00011 011011',
            cpu,
            **kwargs
        )

    def execute(self, statement: MIPSStatement) -> None:
        """Signed integer modulo"""
        self._execute_prechecks(statement)
        fields = self._get_fields(statement)

        # MOD performs a signed 32-bit integer modulo,
        # and places the 32-bit quotient result in GPR[rd].
        rd_address = fields['rd'].value

        rs_address = fields['rs'].value
        rs_value = self._cpu.gpr.read_integer(addr=rs_address, signed=False)

        rt_address = fields['rt'].value
        rt_value = self._cpu.gpr.read_integer(addr=rt_address, signed=False)

        try:
            res = rs_value % rt_value
        except ZeroDivisionError:
            raise mips_exceptions.DivideByZeroException()

        self._cpu.gpr.write_integer(res, addr=rd_address)

# TODO: Rest of MIPS32 v6 Instruction Set
