from Pyssembler.simulator import Simulator
from Pyssembler.simulator.errors import *

prefix = 'work/'

def parse_dat(filename):
   output = []
   with open(filename, 'r') as f:
      print(type(f))
      for line in f.readlines():
         output.append(line.replace('\n', ''))
   return output

if __name__ == '__main__':

   sim = Simulator(debug_mode=True)
   
   #sim.assemble([prefix+'test.asm'])
   #sim.simulate(sim.SINGLE_INSTRUCTION)
   print(sim.CP0.get_regs())

   '''
   for addr, values in sim.memory.dump(radix=bin).items():
      print('{}: {}'.format(addr, ', '.join(values)))
   '''

