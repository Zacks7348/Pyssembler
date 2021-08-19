from Pyssembler.mips.hardware.exceptions import AddressErrorException, MIPSException, MIPSExceptionCodes, SyscallException
import json
import os.path
import ast
import sys
import logging

from ..hardware import registers, memory
from .sim_functions import get_sim_function_by_mnemonic
from .errors import *
from .syscall import simulate_syscall
import config

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

        self.output_buffer = []
    
    def __output_registers(self):
        reg_dump = registers.gpr_dump()
        reg_names = list(reg_dump.keys())
        reg_dumps = ''
        i = 0
        while i < len(reg_names):
            reg_dumps += '[{:<5}: {:>10}]'.format(reg_names[i], reg_dump[reg_names[i]])
            #print(i+1, i+1%4, reg_names[i])
            if (i+1) % 4 == 0: reg_dumps += '\n'
            i += 1

        #regs = ''.join(['[{}: {}]\n'.format(reg, val) for reg, val in registers.gpr_dump().items()])
        LOGGER.info('MIPS32 Registers: \n'+reg_dumps)
    
    def __output_memory(self):
        LOGGER.info(json.dumps(memory.dump(), indent=2))
        #print(json.dumps(memory.dump(), indent=2))
    
    def simulate(self, pc_start=memory.MemoryConfig.text_base_addr):
        registers.pc = pc_start
        registers.gpr_write('$sp', memory.MemoryConfig.stack_pointer)
        registers.gpr_write('$gp', memory.MemoryConfig.global_pointer)
        LOGGER.info(f'Starting simulator at PC={pc_start}...')
        #import pdb; pdb.set_trace()
        if self.states:
            self.__output_registers()
        while not (instr := memory.read_instruction(registers.pc)) is None:
            #import pdb; pdb.set_trace()
            sim_func =  get_sim_function_by_mnemonic(instr.tokens[0].value)
            LOGGER.debug('Executing "{}"...'.format(instr.clean_line))
            try:
                sim_func(instr)
            except AddressErrorException as e:
                print(e.message, e.address)
                return
            except SyscallException as e:
                try:
                    simulate_syscall(e.code)
                except SimulationExitException as sim_exit:
                    if sim_exit.result:
                        LOGGER.info('Exited with value: {}'.format(sim_exit.result))
                        return
                    LOGGER.info('Exited')
                    return
            LOGGER.debug('Finished!')
            if self.states:
                self.__output_registers()
            if self.step:
                while True:
                    cmd = input()
                    cmd = cmd.lower()
                    if cmd == 'next' or cmd == 'n':
                        break
                    elif cmd == 'show registers':
                        self.__output_registers()
                    elif cmd == 'show memory':
                        self.__output_memory()
                    elif cmd == 'quit' or cmd == 'q':
                        return
                    else: continue
            registers.increment_pc()
        LOGGER.info('Stopping simulation: Program dropped off')
