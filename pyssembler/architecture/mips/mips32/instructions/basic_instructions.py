from __future__ import annotations
import typing

from .instruction_set import mips32_instruction
from pyssembler.architecture.mips.common import mips_exceptions, mips_enums
from pyssembler.architecture.mips.common.instruction import *
from pyssembler.architecture.mips.common.hardware import constants
from pyssembler.architecture.utils import numeric

if typing.TYPE_CHECKING:
    from ..cpu import MIPS32CPU
    from pyssembler.architecture.mips.common.statement import MIPSStatement


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
class MIPS32BalcInstruction(MIPSBaseCompactBranchInstruction):
    def __init__(self, cpu: MIPS32CPU, **kwargs):
        super().__init__(
            'balc',
            'Branch and Link, Compact',
            'balc offset',
            'Do an unconditional PC-relative procedure call',
            'GPR[31] = PC + 4; PC = PC + 4 + offset',
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
