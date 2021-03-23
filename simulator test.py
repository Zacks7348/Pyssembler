from Simulator import SingleCycleSimulator

prefix = 'asm/'

def parse_dat(filename):
   output = []
   with open(filename, 'r') as f:
      print(type(f))
      for line in f.readlines():
         output.append(line.replace('\n', ''))
   return output

if __name__ == '__main__':
   sim = SingleCycleSimulator(debug_mode=True)
   #sim.load_instructions(parse_dat('test.dat'))
   #sim.assemble(['basic test.asm'])
   sim.assemble([prefix+'test with data segment.asm'])
   sim.print_reg()
