from Pyssembler.mips.hardware.exceptions import AddressErrorException, MIPSException, MIPSExceptionCodes
import json
from os import name
import os.path
import ast

from ..hardware import registers, memory
from .sim_functions import get_sim_function_by_mnemonic
from .errors import *


class Simulator:
    """
    Base Class for MIPS32 Simulators

    Provides all core components of a MIPS simulator. Also provides a function
    to assemble mips instructions
    """

    def __init__(self, step=False, states=False, verbose=0) -> None:

        # If step=True, wait for user input before executing next instr
        self.step = step
        self.states = states
        self.__verbose = verbose
    
    def __log(self, message: str, verbose: int):
        # Shortcut for logging verbose messages
        if self.__verbose >= verbose:
            print(f'[SIM] {message}')

    def __output_registers(self):
        cnt = 0
        for reg, val in registers.gpr_dump().items():
            if cnt < 4:
                print('[{:<6}: {:>6}]'.format(reg, val), end=' ')
                cnt += 1
            else:
                cnt = 0
                print('[{:<6}: {:>6}]'.format(reg, val))
        print()
    
    def __output_memory(self):
        print(json.dumps(memory.dump(), indent=2))
    
    def simulate(self, pc_start=memory.MemoryConfig.text_base_addr):
        registers.pc = pc_start
        registers.gpr_write('$sp', memory.MemoryConfig.stack_base_addr)
        registers.gpr_write('$gp', memory.MemoryConfig.global_pointer)
        self.__log(f'Starting simulation at {pc_start}', 1)
        while not (instr := memory.read_instruction(registers.pc)) is None:
            sim_func =  get_sim_function_by_mnemonic(instr.tokens[0].value)
            self.__log('Executing {}...'.format(repr(instr.source.line)), 2)
            try:
                sim_func(instr)
            except AddressErrorException as e:
                print(e.message, e)
                return
            self.__log('Finished!', 2)
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
        self.__log('Stopping simulation: Program dropped off', 1)




    