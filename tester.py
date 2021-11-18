from Pyssembler.mips.mips_program import MIPSProgram
from Pyssembler.mips.instructions import instruction_set as instr_set
from Pyssembler import tokenize_program

def main():
    program = MIPSProgram(main='Pyssembler/work/function_with_stack.asm')
    tokenize_program(program)
    for line in program:
        print(line.label, line.tokens)

if __name__ == '__main__':
    main()

