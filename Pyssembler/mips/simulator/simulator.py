from Pyssembler.mips.hardware.exceptions import AddressErrorException, ArithmeticOverflowException, MIPSException, MIPSExceptionCodes, SyscallException
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

    def __init__(self, step=False, states=False) -> None:

        # If step=True, wait for user input before executing next instr
        self.step = step
        self.states = states

    def __output_registers(self):
        reg_dump = GPR.dump()
        reg_names = list(reg_dump.keys())
        reg_dumps = ''
        i = 0
        while i < len(reg_names):
            reg_dumps += '[{:<5}: {:>10}]'.format(
                reg_names[i], reg_dump[reg_names[i]])
            #print(i+1, i+1%4, reg_names[i])
            if (i+1) % 4 == 0:
                reg_dumps += '\n'
            i += 1

        #regs = ''.join(['[{}: {}]\n'.format(reg, val) for reg, val in registers.gpr_dump().items()])
        LOGGER.info('MIPS32 Registers: \n'+reg_dumps)

    def __output_memory(self):
        LOGGER.info(json.dumps(memory.dump(), indent=2))
        #print(json.dumps(memory.dump(), indent=2))

    def __init_cpu(self, pc_start):
        GPR.pc = pc_start
        GPR.write('$sp', memory.MemoryConfig.stack_pointer)
        GPR.write('$gp', memory.MemoryConfig.global_pointer)

    def simulate(self, pc_start=memory.MemoryConfig.text_base_addr):
        """
        Starts simulation of mips program. Will continue reading instructions
        at MEM[PC] until an exit syscall is executed or the program drops off
        (there is no instruction at MEM[PC]). 

        The simulator works by getting the associated sim function of the
        instruction and calling it. Each sim function will perform it's logic
        and raise a MIPSException if neccessary. These exceptions are caught here
        and will transfer control to the exception handler.

        Attributes
        ----------
        pc_start: int, default=memory.MemoryConfig.text_base_addr
            The first instruction address of the program
        """
        self.__init_cpu(pc_start)
        LOGGER.info(f'Starting simulator at PC={pc_start}...')
        while not (instr := memory.read_instruction(GPR.pc)) is None:
            sim_func = get_sim_function_by_mnemonic(instr.tokens[0].value)
            LOGGER.debug('Executing "{}"...'.format(instr.clean_line))
            try:
                sim_func(instr)
            except MIPSException as e:
                res = self.exception_handler(e)
                if res == 0:
                    LOGGER.info('Exiting...')
                    return
            LOGGER.debug('Finished!')
            if self.states:
                self.__output_registers()
            if self.step:
                while True:
                    cmd = input().lower()
                    if cmd == 'next' or cmd == 'n':
                        break
                    elif cmd == 'show registers':
                        self.__output_registers()
                    elif cmd == 'show memory':
                        self.__output_memory()
                    elif cmd == 'quit' or cmd == 'q':
                        return
                    else:
                        continue
            GPR.increment_pc()
        LOGGER.info('Stopping simulation: Program dropped off')

    def exception_handler(self, exception: MIPSException):
        """
        The default exception handler. Performs neccessary actions based on the
        exception code in exception. Returns 0 to exit simulation
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
            return 0
        return 1
        
