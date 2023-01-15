from typing import Dict, List

from pyssembler.utils import LoggableMixin
from .hardware import MIPSMemory, MIPSRegister
from .states import State


class MIPSCPU(LoggableMixin):
    """
    This class provides logic for simulating a MISP32 CPU.
    """
    MIPS_32BIT = '32'
    MIPS_64BIT = '64'

    def __init__(self):
        self._log = self._get_logger()

        # Registers
        self._pc: MIPSRegister = MIPSRegister(None, 'PC')
        self._gp_registers: Dict[int, MIPSRegister] = {}  # General Purpose Registers
        self._cp0_registers: Dict[int, MIPSRegister] = {}  # Coprocessor 0 Registers
        self._cp1_registers: Dict[int, MIPSRegister] = {}  # Coprocessor 1 Registers
        self._cp2_registers: Dict[int, MIPSRegister] = {}  # Coprocessor 2 Registers (Not implemented)
        self._cp3_registers: Dict[int, MIPSRegister] = {}  # Coprocessor 3 Registers (Not implemented)
        self._register_name_map: Dict[str, MIPSRegister] = {}

        # Memory
        self._memory: MIPSMemory = MIPSMemory()

        # State History
        self._current_state: State = None

        self._current_program = None

    @property
    def current_state(self):
        return self._current_state

    @property
    def pc(self):
        return self._pc.read()

    def load_program(self, program):
        """
        Load the program into this CPU's simulated memory.

        The following preprocessing steps will be performed before the program
        is loaded into memory:

        1. Tokenization
            Each ASM file is ran through the tokenizer to generate a list
            of MIPS statements.
        2. Generate Symbol Tables
            A global symbol table will be generated for the program as well
            as additional local symbol tables per ASM file.
        3. Directives
            Directives are handled and any data will be written to the static
            user data segment of memory.
        4. Encoding
            Each MIPS instruction statement is encoded into its binary
            representation and written into the user text segement of memory.

        :param program: The program to load
        :type program: MIPSProgram
        :return: None
        """
        pass

    def read_register(self, name: str, signed=False):
        if name not in self._register_name_map:
            raise ValueError(f'No register found with name {name}')
        return self._register_name_map[name].read(signed=signed)

    def _save_current_state(self):
        if self._current_state is None:
            self._current_state = State()
            for register in self._iter_registers():
                self._current_state.registers[register.name] = register.read()

            self._current_state.memory = self._memory.memory
            return

        new_state = State()
        for register in self._iter_registers():
            if register.read() != self._current_state.last_register_value(register.name):
                new_state.registers[register.name] = register.read()

        for address, value in self._memory.memory.items():
            if value != self._current_state.last_memory_value(address):
                new_state.memory[address] = value

        new_state.prev_state = self._current_state
        self._current_state.next_state = new_state
        self._current_state = new_state

    def _iter_registers(self):
        yield from self._gp_registers.values()
        yield from self._cp0_registers.values()
        yield from self._cp1_registers.values()
        yield from self._cp2_registers.values()
        yield from self._cp3_registers.values()

    def _init_registers(self):
        # General-Purpose Registers
        self._gp_registers = {
            0: MIPSRegister(0, '$zero', read_only=True),
            1: MIPSRegister(1, '$at'),
            2: MIPSRegister(2, '$v0'),
            3: MIPSRegister(3, '$v1'),
            4: MIPSRegister(4, '$a0'),
            5: MIPSRegister(5, '$a1'),
            6: MIPSRegister(6, '$a2'),
            7: MIPSRegister(7, '$a3'),
            8: MIPSRegister(8, '$t0'),
            9: MIPSRegister(9, '$t1'),
            10: MIPSRegister(10, '$t2'),
            11: MIPSRegister(11, '$t3'),
            12: MIPSRegister(12, '$t4'),
            13: MIPSRegister(13, '$t5'),
            14: MIPSRegister(14, '$t6'),
            15: MIPSRegister(15, '$t7'),
            16: MIPSRegister(16, '$s0'),
            17: MIPSRegister(17, '$s1'),
            18: MIPSRegister(18, '$s2'),
            19: MIPSRegister(19, '$s3'),
            20: MIPSRegister(20, '$s4'),
            21: MIPSRegister(21, '$s5'),
            22: MIPSRegister(22, '$s6'),
            23: MIPSRegister(23, '$s7'),
            24: MIPSRegister(24, '$t8'),
            25: MIPSRegister(25, '$t9'),
            26: MIPSRegister(26, '$k0'),
            27: MIPSRegister(27, '$k1'),
            28: MIPSRegister(28, '$gp'),
            29: MIPSRegister(29, '$sp'),
            30: MIPSRegister(30, '$fp'),
            31: MIPSRegister(31, '$ra'),
        }

        # Coprocessor 0 Registers
        self._cp0_registers = {
            8: MIPSRegister(8, '$badvaddr'),
            9: MIPSRegister(9, '$count'),
            11: MIPSRegister(11, '$compare'),
            12: MIPSRegister(12, '$status'),
            13: MIPSRegister(13, '$cause'),
            14: MIPSRegister(14, '$exceptionpc'),
            15: MIPSRegister(15, '$prid'),
            16: MIPSRegister(16, '$config'),
            30: MIPSRegister(30, '$errorpc')
        }

        # Coprocessor 1 Registers (FPU)
        # TODO: Implement

        # Coprocessor 2 Registers
        # NOT IMPLEMENTED - Available for custom implementations

        # Coprocessor 3 Registers
        # NOT IMPLEMENTED - FPU for MIPS64 Architecture

        for register in self._iter_registers():
            self._register_name_map[register.name] = register

        self._register_name_map[self._pc.name] = self._pc

    def _execute_instruction(self):
        pass
