from Pyssembler.simulator import Simulator
from Pyssembler.simulator.instruction import InstructionSet
from Pyssembler.simulator.hardware import MEM, RF
from Pyssembler.simulator.utils import Binary
import json
#from Pyssembler.simulator.errors import *


prefix = 'work/'

if __name__ == '__main__':

   sim = Simulator(debug_mode=True)
   
   sim.assemble([prefix+'test.asm'])
   sim.simulate()