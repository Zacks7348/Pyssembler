from abc import abstractmethod
from textwrap import dedent
import time
import typing

from pyssembler.core.architecture.base import PyssemblerCPU
from pyssembler.core.architecture.exceptions import *
from pyssembler.core.architecture import SourceLine
from pyssembler.utils import LoggableMixin

CPUType = typing.TypeVar('CPUType', bound=PyssemblerCPU)

__all__ = ['PyssemblerSimulatorBase', 'CPUType']


class PyssemblerSimulatorBase(typing.Generic[CPUType], LoggableMixin):
    """Base class implementing the core framework for simulating a CPU."""

    def __init__(self, cpu: CPUType, debug: bool = False):
        self._cpu: CPUType = cpu
        self._debug: bool = debug
        self._breakpoints: typing.List[SourceLine] = []
        self._stepping: bool = False
        self._first_instr_flag: bool = True

        self._log = self.get_logger()

    @property
    def is_stepping(self) -> bool:
        return self._stepping

    def do_stepping(self, flag: bool):
        self._stepping = flag

    def set_breakpoint(self, line: SourceLine):
        """Add a breakpoint."""
        if line in self._breakpoints:
            return

        self._breakpoints.append(line)

    def remove_breakpoint(self, line: SourceLine):
        """Remove a breakpoint."""
        self._breakpoints.remove(line)

    def clear_breakpoint(self):
        """Clear all breakpoints."""
        self._breakpoints.clear()

    def run(self):
        """Run the simulation."""
        self._first_instr_flag = True
        while True:
            try:
                self._step_execution()

            except ProgramStopped as e:
                self._log.info(e)
                break

    def _step_execution(self):
        """Perform a single execution step.

        If debugging is enabled then the debugger will be launched if:
            1. This is the first statement of the program
            2. The statement to be executed is declared a breakpoint
            3. Stepping is enabled.
            4. The program crashes or drops off.
        """
        statement = self._cpu.get_current_statement()
        if statement is not None:
            line = SourceLine(None, statement.tokens[0].src_line, statement.tokens[0].src_file)
            if self._debug and (self._is_breakpoint(line) or self._first_instr_flag):
                self._log.debug(f'Debug point reached.')
                self._debugger()

        try:
            self._cpu.step_execution()
            self._first_instr_flag = False

            if self._stepping:
                self._debugger()

        except (ProgramException, ProgramDroppedOff) as e:

            if self._debug:
                self._log.error(e)
                self._debugger()

            else:
                raise

    def _is_breakpoint(self, line: SourceLine) -> bool:
        """Returns True if the line is a breakpoint."""
        for breakpoint_src in self._breakpoints:
            if breakpoint_src == line:
                return True

        return False

    @abstractmethod
    def _debugger(self):
        """Entry point to the debugger. This should be implemented by the subclass."""
        ...
