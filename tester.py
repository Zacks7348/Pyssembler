from Pyssembler.mips.mips_program import MIPSProgram
from Pyssembler.mips.instructions import instruction_set as instr_set
from Pyssembler import Assembler, Simulator

def main():
    program = MIPSProgram(main='Pyssembler/work/function_with_stack.asm')
    a = Assembler()
    a.assemble(program)
    s = Simulator(step=True, states=True)
    s.simulate()

if __name__ == '__main__':
    main()

