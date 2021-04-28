from Pyssembler.simulator import Simulator
from Pyssembler.simulator.utils import Binary
from  Pyssembler.mips.instructions import setup_instructions
import json
#from Pyssembler.simulator.errors import *


prefix = 'work/'

if __name__ == '__main__':

   # sim = Simulator(debug_mode=True)
   # sim.assemble([prefix+'simtest.asm'])
   # sim.simulate()
   instructions = setup_instructions()
   print(instructions)