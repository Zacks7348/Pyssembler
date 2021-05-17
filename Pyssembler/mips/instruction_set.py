from .mips_program import MIPSProgram
from enum import Enum

from .mips_exceptions import *
from .hardware import RF, MEM
from .utils import BYTE, Integer
from .instructions import setup_instructions


class InstructionType(Enum):

    R_TYPE = 0
    I_TYPE = 1
    I_B_TYPE = 2
    J_TYPE = 3


class InstructionSet:
    """
    Represents a set of MIPS32 instructions
    """

    def __init__(self):
        self.instructions = setup_instructions()

    def get_instr(self, name):
        return self.instructions.get(name, None)
    
    def encode_program(self, program: MIPSProgram):
        """
        #TODO: move logic for assembling here
        """



