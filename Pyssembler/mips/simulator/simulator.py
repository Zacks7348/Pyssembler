from Pyssembler.mips.hardware.exceptions import MIPSException, MIPSExceptionCodes, SyscallException
import json
import os.path
import ast
import sys
import logging

from ..hardware import GPR, CP0, memory
from .sim_functions import get_sim_function_by_mnemonic
from .errors import *
from .syscall import simulate_syscall

LOGGER = logging.getLogger('PYSSEMBLER.SIMULATOR')
SIM_OUTPUT = logging.getLogger('SIMULATOR_OUTPUT')


class Simulator:
    """
    Base Class for MIPS32 Simulators

    Provides all core components of a MIPS simulator. Also provides a function
    to assemble mips instructions
    """

    def __init__(self) -> None:

        # If step=True, wait for user input before executing next instr
        self.__step = False

    def start(self, pc_start=memory.MemoryConfig.text_base_addr, step=False):
        """
        Starts MIPS32 simulator.

        Attributes
        ----------
        pc_start: int, default=memory.MemoryConfig.text_base_addr
            The first instruction address of the program
        step: bool, default=False
            If False, runs the entire simulation until the program stops. Setting to True
            allows to run each execution step with the execute_instruction function
        """
        self.__step = step

        # Set up the environment
        GPR.pc = pc_start
        GPR.write('$sp', memory.MemoryConfig.stack_pointer)
        GPR.write('$gp', memory.MemoryConfig.global_pointer)

        LOGGER.info(f'Starting simulator at PC={pc_start}...')
        if self.__step:
            return
        while True:
            try:
                self.execute_instruction()
            except SimulationExitException:
                # Program stopped executing
                return

    def execute_instruction(self):
        """
        Executes the instruction located at PC

        Raises a SimulationExitException if the program stops. This
        could be caused by the following reasons:
        - Program dropped off
        - Exit system call was executed
        - Unhandled exception

        Returns the address of the instruction executed
        """
        instr = memory.read_instruction(GPR.pc)
        if not instr:
            # No instruction at PC, program dropped off
            raise SimulationExitException('Program Dropped Off')
        sim_func = get_sim_function_by_mnemonic(instr.tokens[0].value)
        try:
            sim_func(instr)
        except MIPSException as e:
            # May Raise SimulationExitException, let it bubble up
            self.exception_handler(e)
        GPR.increment_pc()
        return instr.memory_addr

    def exception_handler(self, exception: MIPSException):
        """
        The default exception handler. Performs necessary actions based on the
        exception code in exception.

        Raises SimulationExitException if there is no exception handler written to
        memory
        """

        # Set CP0 STATUS Register Exception Level bit
        CP0.write_status(exc_lvl=1)
        # Set CP0 CAUSE Register Exception Code
        CP0.write_cause(exc_code=exception.exception_type)
        # Write current PC to CP0 EPC
        CP0.write(CP0.EPC, GPR.pc)
        # If invalid memory address caused exception, set CP0 VADDR Register
        if exception.exception_type == MIPSExceptionCodes.ADDRL:
            CP0.write(CP0.VADDR, exception.address)
        if exception.exception_type == MIPSExceptionCodes.ADDRS:
            CP0.write(CP0.VADDR, exception.address)

        if not memory.read_instruction(memory.MemoryConfig.ktext_base_addr):
            # No exception handler was written to memory
            LOGGER.info(str(exception))
            raise SimulationExitException(0)
        
