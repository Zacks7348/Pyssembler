from Pyssembler.mips.hardware import memory
from Pyssembler.mips import utils
from ctypes import c_int32, c_uint32
import json

from Pyssembler.mips.mips_program import MIPSProgram
from Pyssembler.mips.assembler import Assembler
from Pyssembler.mips.instructions import instruction_set as instr_set
#from Pyssembler.mips.hardware import memory, registers
import tests
from Pyssembler.mips.tokenizer import tokenize_program

from Pyssembler.mips.simulator import sim_functions
from Pyssembler.mips.simulator import Simulator


def main():
    program = MIPSProgram(main='Pyssembler/work/function_with_stack.asm')
    tokenize_program(program)
    for line in program:
        instr = instr_set.match_instruction(line)
        print(line, '\n', instr, '\n\n')

if __name__ == '__main__':
    main()

