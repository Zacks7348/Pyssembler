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

# def generate_sim_functions(filename):
#     def write_function(name):
#         template = 'def {func_name}(instr: int) -> None:\n\t"""\n\tMIPS32 {name} simulation function\n\t"""\n\tpass\n\n'
#         with open(filename, 'a') as f:
#             f.write(template.format(func_name=name+'_instruction', name=name))
#             print('Generated function {}'.format(name))
#     with open(filename, 'w') as f:
#         f.write('import inspect\nimport sys\nfrom typing import Callable\n')
#         f.write(
# """\"\"\"
# MIPS32 simulation functions are placed here\n
# The names of the functions should match the 
# instruction mnemonic followed by _instruction
# For example: def add_instruction()
# \"\"\"\n\n""")
#         f.write(
# """def get_sim_function_by_name(instr_name: str) -> Callable[[int], None]:
#     \"\"\"
#     Function for getting an instructions simulation function by mnemonic
#     \"\"\"
#     for name, obj in inspect.getmembers(sys.modules[__name__]):
#         if name == instr_name.replace('_instruction', '') and inspect.isfunction(obj):
#             return obj\n\n""")
#     for instr in InstructionSet.instructions:
#         write_function(instr.mnemonic)

# def test_assembly():
#     #memory.set_verbose(1)

#     program = MIPSProgram(main='test.asm')
#     asm = Assembler()
#     asm.assemble(program)

#     for segment, statements in asm.segment_contents.items():
#         print(segment)
#         for s in statements:
#             print(s, s.memory_addr)
#             print('\t', s.get_binary_instr_segmented())
#         print()
    
#     print(program.global_symbols.table)
#     for table in program.local_symbols.values():
#         print(table.table)

#     print('-----MEMORY-----')
#     for addr, values in memory.dump().items():
#         print('{}: {}'.format(addr, values))

# def test_tokenization():
#     program = MIPSProgram(main='test.asm')
#     # for line in program.src_lines:
#     #     print(repr(line.line))
#     tokenize_program(program)

#     print('PRINTING PROGRAM LINES')
#     for line in program:
#         print(line)
#         for token in line.tokens:
#             print('\t', token)

if __name__ == '__main__':
    #generate_sim_functions('Pyssembler/mips/instructions/sim_functions.py')
    # program = MIPSProgram(main='func_test.asm')
    # asm = Assembler()
    # asm.assemble(program)
    # for instr in program:
    #     print('Simulating '+instr.tokens[0].value)
    #     sim = get_sim_function_by_mnemonic(instr.tokens[0].value)
    #     sim(instr)
    # print(registers.gpr_dump())
    program = MIPSProgram(main='test.asm')
    asm = Assembler()
    asm.assemble(program)
    for instr in program:
        print(instr)
        print(instr.tokens)
        print()

