from Pyssembler.simulator import Simulator
from Pyssembler.simulator.utils import Binary
from  Pyssembler.mips.instruction_set import InstructionSet
from Pyssembler.mips.mips_program import MIPSProgram
import json
#from Pyssembler.simulator.errors import *


prefix = 'work/'

if __name__ == '__main__':

   # sim = Simulator(debug_mode=True)
   # sim.assemble([prefix+'simtest.asm'])
   # sim.simulate()

   # instr_set = InstructionSet()
   # print(repr(instr_set.get_instr('add')))
   # bin_instr = instr_set.get_instr('add').encode('add $4, $s2, $t3')
   # print(bin_instr, len(bin_instr))
   program = MIPSProgram([prefix+'test.asm'])
   for line, num in program.program[prefix+'test.asm']:
      print(line, num)
   program.prepare()
   print('-------------')
   for line in program.code:
      print(line)