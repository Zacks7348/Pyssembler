from __future__ import annotations
from abc import abstractmethod
import typing

from .mips_exceptions import *
from pyssembler.architecture import core

if typing.TYPE_CHECKING:
    from ..common.assembler import MIPSAssembler
    from .hardware.memory import MIPSMemory
    from .hardware.register import MIPSRegister, MIPSRegisterFile


class MIPSCPU(core.PyssemblerCPU):

    def __init__(self, delay_slots: bool = False):
        super().__init__()
        self._do_delay_slots: bool = delay_slots
        self._loop_limit: int = 100
        self._loop_tracker: typing.Dict[int, int] = {}

        # Prevent Circular dependency
        from ..common.assembler import MIPSAssembler
        self._assembler: MIPSAssembler = MIPSAssembler(self)

    @property
    def assembler(self) -> MIPSAssembler:
        return self._assembler

    @property
    def do_delay_slots(self) -> bool:
        return self._do_delay_slots

    @property
    @abstractmethod
    def pc(self) -> MIPSRegister:
        ...

    @property
    @abstractmethod
    def gpr(self) -> MIPSRegisterFile:
        ...

    @property
    @abstractmethod
    def fpr(self) -> MIPSRegisterFile:
        ...

    @property
    @abstractmethod
    def memory(self) -> MIPSMemory:
        ...

    def enable_delay_slots(self) -> None:
        self._do_delay_slots = True

    def disable_delay_slots(self) -> None:
        self._do_delay_slots = False

    def get_pc_instruction(self, offset: int = 0):
        return self.memory.read_instruction(self.pc.read_integer() + (offset * 4))

    def increment_pc(self):
        self.pc.write_integer(self.pc.read_integer() + 4)

    def execute(self) -> None:
        while True:
            self.step_execution()

    def step_execution(self) -> None:
        self._step()

    def execute_instruction_at_address(self, addr: int, delay_slot: bool = False):
        # Get instruction at address
        instr = self.memory.read_instruction(addr)

        # Check if program dropped off (No instruction at memory address)
        if instr is None:
            raise core.ProgramDroppedOff(addr)

        # Check if this a CTI in a delay slot
        if self.do_delay_slots:
            # Import here to protect against circular imports
            from .instruction import MIPSControlTransferInstruction

            if delay_slot and isinstance(instr.instr_impl, MIPSControlTransferInstruction):
                raise ReservedInstructionException()

        # Update loop tracker
        cnt = self._loop_tracker.get(instr.address, 0)
        if cnt >= self._loop_limit:
            raise core.ProgramStopped(f'Loop Limit ({self._loop_limit}) exceeded at address 0x{instr.address:08x}')
        self._loop_tracker[instr.address] = cnt + 1

        # Execute instruction
        self._log.debug(f'Executing instruction "{instr}" at address 0x{instr.address:08x}...')
        instr.execute()

    def _step(self) -> None:
        """Perform an execution cycle"""

        # Execute instruction at PC
        # Let any core Exceptions bubble up
        try:
            self.execute_instruction_at_address(self.pc.read_integer())

        except MIPSException as e:
            # TODO: Exception Handler
            raise core.ProgramCrashed(e.msg)

        # Update PC
        self.increment_pc()

    @abstractmethod
    def get_register_address(self, name: str) -> int:
        ...
