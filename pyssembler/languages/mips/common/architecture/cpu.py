from __future__ import annotations
from abc import abstractmethod
import typing

from .mips_exceptions import *
from pyssembler.core.architecture.base import PyssemblerCPU
from pyssembler.core.architecture.exceptions import ProgramCrashed, ProgramDroppedOff, ProgramStopped

if typing.TYPE_CHECKING:
    from .assembler import MIPSAssembler
    from .statement import MIPSStatement
    from .hardware.memory import MIPSMemory
    from .hardware.register import MIPSRegister, MIPSRegisterFile
    from .mips_program import MIPSProgram, AssemblyFile


class MIPSCPU(PyssemblerCPU):

    def __init__(self, delay_slots: bool = False):
        super().__init__()
        self._do_delay_slots: bool = delay_slots
        self._loop_limit: int = 100
        self._loop_tracker: typing.Dict[int, int] = {}
        self._frames = []
        self._currently_loaded_program: MIPSProgram = None
        self._last_executed_statement: MIPSStatement = None

        # Prevent Circular dependency
        from .assembler import MIPSAssembler
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

    def get_pc_instruction(self, offset: int = 0) -> MIPSStatement:
        return self.memory.read_instruction(self.pc.read_integer() + (offset * 4))

    def increment_pc(self):
        self.pc.write_integer(self.pc.read_integer() + 4)

    def execute(self) -> None:
        while True:
            self.step_execution()

    def step_execution(self) -> None:
        self._step()

    def get_current_file(self) -> AssemblyFile:
        statement = self.get_current_statement()
        if statement is not None:
            return statement.src.asm_file

        statement = self.get_last_executed_statement()
        if statement is not None:
            return statement.src.asm_file

        return None

    def get_last_executed_statement(self) -> MIPSStatement:
        return self._last_executed_statement

    def get_current_statement(self) -> MIPSStatement:
        return self.get_pc_instruction()

    def get_current_statement_address(self) -> int:
        return self.pc.read_integer()

    def get_current_program(self) -> MIPSProgram:
        return self._currently_loaded_program

    def execute_instruction_at_address(self, addr: int, delay_slot: bool = False):
        # Get instruction at address
        instr = self.memory.read_instruction(addr)

        # Check if program dropped off (No instruction at memory address)
        if instr is None:
            raise ProgramDroppedOff(addr)

        # Check if this a CTI in a delay slot
        if self.do_delay_slots:
            # Import here to protect against circular imports
            from .instruction import MIPSControlTransferInstruction

            if delay_slot and isinstance(instr.instr_impl, MIPSControlTransferInstruction):
                raise ReservedInstructionException()

        # Update loop tracker
        cnt = self._loop_tracker.get(instr.address, 0)
        if cnt >= self._loop_limit:
            raise ProgramStopped(f'Loop Limit ({self._loop_limit}) exceeded at address 0x{instr.address:08x}')
        self._loop_tracker[instr.address] = cnt + 1

        # Execute instruction
        self._log.debug(f'Executing instruction "{instr}" at address 0x{instr.address:08x}...')
        instr.execute()
        self._last_executed_statement = instr

    def _step(self) -> None:
        """Perform an execution cycle"""

        # Execute instruction at PC
        # Let any core Exceptions bubble up
        try:
            self.execute_instruction_at_address(self.pc.read_integer())

        except MIPSException as e:
            # TODO: Exception Handler
            raise ProgramCrashed(e.msg)

        # Update PC
        self.increment_pc()

    @abstractmethod
    def get_register_address(self, name: str) -> int:
        ...

    def _set_currently_loaded_program(self, program: MIPSProgram) -> None:
        self._currently_loaded_program = program
