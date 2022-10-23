from typing import Dict, List

from pyssembler.utils import LoggableMixin
from .hardware import MIPSRegister
from .states import State


class MIPSEngine(LoggableMixin):
    MIPS_32BIT = '32'
    MIPS_64BIT = '64'

    def __init__(self):
        self._log = self._get_logger()

        # Registers
        self._pc: MIPSRegister = MIPSRegister(None, 'PC')
        self._gp_registers: Dict[int, MIPSRegister]  = {}  # General Purpose Registers
        self._cp0_registers: Dict[int, MIPSRegister] = {}  # Coprocessor 0 Registers
        self._cp1_registers: Dict[int, MIPSRegister] = {}  # Coprocessor 1 Registers
        self._cp2_registers: Dict[int, MIPSRegister] = {}  # Coprocessor 2 Registers (Not implemented)
        self._cp3_registers: Dict[int, MIPSRegister] = {}  # Coprocessor 3 Registers (Not implemented)
        
        self._register_name_map: Dict[str, MIPSRegister] = {}

        # Memory

        # State History
        self.current_state = None

    def load_program(self):
        """
        Load the program into the MIPS simulation engine.
        :return:
        """
        pass

    def reset(self):
        pass

    def start(self):
        pass

    def pause(self):
        pass

    def stop(self):
        pass

    def read_register(self, name: str, signed=False):
        if name not in self._register_name_map:
            raise ValueError(f'No register found with name {name}')
        return self._register_name_map[name].read(signed=signed)

    def dump(self):
        pass

    def _save_current_state(self):
        if self.current_state is None:
            pass

    def _iter_registers(self):
        yield from self._gp_registers.values()
        yield from self._cp0_registers.values()
        yield from self._cp1_registers.values()
        yield from self._cp2_registers.values()
        yield from self._cp3_registers.values()

    def _init_registers(self):
        # General-Purpose Registers
        self._gp_registers = {
            0:  MIPSRegister(0,  '$zero', read_only=True),
            1:  MIPSRegister(1,  '$at'),
            2:  MIPSRegister(2,  '$v0'),
            3:  MIPSRegister(3,  '$v1'),
            4:  MIPSRegister(4,  '$a0'),
            5:  MIPSRegister(5,  '$a1'),
            6:  MIPSRegister(6,  '$a2'),
            7:  MIPSRegister(7,  '$a3'),
            8:  MIPSRegister(8,  '$t0'),
            9:  MIPSRegister(9,  '$t1'),
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
            8 : MIPSRegister(8,  '$badvaddr'),
            9 : MIPSRegister(9,  '$count'),
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

        for regiser in self._iter_registers():
            self._register_name_map[regiser.name] = regiser

        self._register_name_map[self._pc.name] = self._pc










