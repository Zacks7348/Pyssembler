import json
import sys
import ast

from .utils import bin2int, clean_code, int2bin
from .utils import WORD, HWORD, BYTE, BIT
from .instruction import Instruction
from .hardware import Memory, RegisterFile
from .hardware.coprocessors import CP0

class Simulator:
    """
    Base Class for MIPS32 Simulators

    Provides registers and memory
    """
    def __init__(self, step=False, debug_mode=False, prefix='[Simulator]') -> None:
        # If step=True, wait for user input before executing next instr
        self.step = step
        self.debug_mode = debug_mode
        self.verbose_prefix = prefix

        # Memory
        self.memory = Memory()

        #Coprocessors
        self.CP0 = CP0()

        # Gen Purpose Registers
        self.rf = RegisterFile()
        self.rf.write(name='$gp', val=self.memory.global_pointer)
        self.rf.write(name='$sp', val=self.memory.stack_base_addr)
        self.rf.PC = self.memory.text_base_addr

    def mem_write(self, addr: int, val: str):
        try:
            self.memory.write(addr, val)
        except Exception as err:
            self.error('Could not write to memory, '+str(err))

    def load_instructions(self, instructions: list) -> None:
        """
        Takes a list of instructions and stores them into simulated memory
        """
        self.debug('Loading instructions into memory...')
        for i, instr in enumerate(instructions):
            self.memory.write(self.rf.PC + (i*4), instr)
            self.debug('Loaded {}/{} instructions into memory'.format(
                i+1, len(instructions)))

    def debug(self, message: str) -> None:
        if self.debug_mode:
            print('{}[DEBUG] {}'.format(self.verbose_prefix, message))

    def warning(self, message: str) -> None:
        print('{}[WARNING] {}'.format(self.verbose_prefix, message))
    
    def error(self, message: str) -> None:
        print('{}[ERROR] {}'.format(self.verbose_prefix, message))

    def print_reg(self, radix=int):
        print('-------Registers-------')
        self.rf.print(radix)
        print('-----------------------')
    
class SingleCycleSimulator(Simulator):
    """
    Represents a Single Cycle MIPS32 Simulator. 

    """
    def __init__(self, step=False, debug_mode=False) -> None:
        super().__init__(step=step, debug_mode=debug_mode, prefix='[SCS]')


    def assemble(self, asm_files: list) -> None:
        self.debug('Assembling files...')
        self.global_symbols = {}
        self.local_symbols = {} 
        self.asm_files = asm_files
        self.m_code = [] # machine code
        self.a_code = {} # assembly code


        # Clean up asm files and store contents into a_code
        for f in self.asm_files:
            with open(f, 'r') as asm:
                self.a_code[f] = clean_code(asm.readlines())
                for line in self.a_code[f]:
                    print(line)
        
        # Handle any .include directives
        status = self.__include()
        if not status:
            self.error('Could not assemble program')
            return
        
        # Create symbol tables for program. also prepare memory
        # addresses for each instruction
        instructions = self.generate_symbols()
        if not instructions:
            self.error('Could not assemble program')
            return

        # Ready to assemble instructions
            

    def __include(self) -> bool:
        """
        Function to handle any .include directives

        If a file in self.asm_files is found in a .include directive,
        that file is removed from asm_files since all code will now
        be in the current file

        Returns True if successful, otherwise False
        """
        included_files = []
        ignored = {}
        to_include = []
        for f in self.asm_files:
            # if file has been included in another file, skip
            # this file will be removed from asm_files later
            if f in included_files: continue
            ignored[f] = []
            for i, line in enumerate(self.a_code[f]):
                if not line.startswith('.include'):
                    continue
                filename = ' '.join(line.split()[1:])
                if filename == f:
                    # Case when .include is found with filename = current file name
                    # line is deleted from program
                    ignored[f].append(i)
                    self.warning('.include directive trying to include self, ignoring directive')
                try:
                    # Try to open file from include directive
                    with open(filename, 'r') as f_include:
                        # add code from filename to to_include
                        # ([code], i) i is index to add code into
                        to_include.append((clean_code(f_include.readlines()), i))
                except:
                    # Could not open file, return False
                    self.error(
                        'Could not open "{}" from .include directive in "{}"'.format(
                            filename, f
                    ))
                    return False  
                if not filename in included_files:
                    included_files.append(filename)

            for code, i in to_include:
                self.a_code[f] = self.a_code[f][:i] + code + self.a_code[f][i+1:]

        for f in included_files:
            # Remove any included files from asm_files
            if f in self.asm_files: self.asm_files.remove(f)
        return True

    def __assemble(self, instructions: list) -> None:
        pass

    def generate_symbols(self) -> None:
        """
        Generates symbol tables for assembly program
        Creates 1 global symbol table and local
        symbol tables for each file. Checks that syntax is correct
        for label declaration.

        Returns a list of MIPS assembly instructions with corresponding
        text memory addresses.
        """
        sizes = {'.word': WORD, '.half': HWORD, '.byte': BYTE}
        data_addr = self.memory.data_base_addr
        extern_addr = self.memory.extern_base_addr
        in_data = False # Assume we are in text segment until .data read
        PC_offset = 0 # For assigning each instruction a memory location
        instructions = [] # list of mips assembly instructions and addr to be stored in
        for f in self.asm_files:
            self.local_symbols[f] = {}
            for line in self.a_code[f]:
                if line.startswith('.data'): in_data = True
                elif line.startswith('.text'): in_data = False
                elif line.startswith('.globl'):
                    label = line.split()[1]
                    if label in self.global_symbols:
                        # global label already defined
                        self.error('.globl {} already defined'.format(label))
                        return False
                    if label in self.local_symbols[f]:
                        # label has been defined locally already
                        # move it to global table and remove from local table
                        self.global_symbols[label] = self.local_symbols[f][label]
                        del self.local_symbols[f][label]
                    # label has not been defined yet
                    else: self.global_symbols[label] = None
                elif line.startswith('.align'):
                    n = int(line.split()[1])
                    if n > 2:
                        self.error('.align n, n must be 0, 1, 2. Got {}'.format(n))
                        return False
                    if (data_addr % 2**n) != 0: 
                        data_addr += 2**n - (data_addr % 2**n)
                elif line.startswith('.extern'):
                    parsed = line.split()
                    label = parsed[1]
                    num_bytes = parsed[2]
                    self.global_symbols[label] = extern_addr
                    self.debug('Creating extern label {} at mem address'\
                        ' 0x{:08x} of size {} bytes'.format(label, extern_addr, num_bytes))
                    for _ in range(int(num_bytes)):
                        self.mem_write(extern_addr, int2bin(0, bits=BYTE))
                        extern_addr += 1
                
                elif not in_data:
                    # text section
                    # add tuple to instructions: (instr, addr)
                    to_add = line
                    if ':' in line:
                        label = line.split()[0].replace(':', '')
                        to_add = ' '.join(line.split()[1:])
                        if self.global_symbols.get(label, False):
                            # label exists in global table and has already been resolved
                            self.error('Label {} has already been defined globally'.format(label))
                            return False
                        if self.local_symbols[f].get(label, False):
                            # label exists in local table and has already been resolved
                            self.error('Label {} has already been defined locally'.format(label))
                            return False
                        if not self.global_symbols.get(label, True):
                            # label exists in global table but is unresolved
                            self.global_symbols[label] = self.rf.PC + PC_offset
                        else:
                            # label does not exist in global table, add it to local
                            self.local_symbols[f][label] = self.rf.PC + PC_offset
                    instructions.append((to_add, self.rf.PC + PC_offset))
                    PC_offset += 4 # PC + offset points to next empty address

                if not ':' in line: continue
                parsed = line.split()
                if in_data:
                    # labels declared in .data section
                    label = parsed[0].replace(':', '')
                    directive = parsed[1]
                    values = parsed[2:]
                    if directive in sizes:
                        # .word, .half, or .byte directives
                        align = (sizes[directive] // BYTE) # determines alignment
                        if data_addr % align != 0:
                            data_addr += align - (data_addr % align)
                        self.local_symbols[f][label] = data_addr
                        for val in values:
                            if '"' in val:
                                self.error('Cannot store string as word.' \
                                    ' Must use .ascii or .asciiz')
                                return False
                            val = val.replace(',', '')
                            if "'" in val: val = ord(val.replace("'", ''))
                            else: val = int(val)
                            bin_val = int2bin(val, bits=sizes[directive])
                            self.debug('writing {} ({}) into mem at address' \
                                ' 0x{:08x}'.format(bin_val, val, data_addr))
                            self.mem_write(data_addr, bin_val)
                            data_addr += align

                    elif directive == '.ascii' or directive == '.asciiz':
                        self.local_symbols[f][label] = data_addr
                        string = ' '.join(values)
                        string = ast.literal_eval(string)
                        if directive.endswith('z'): string += '\0'
                        for char in string:
                            bin_val = int2bin(ord(char), bits=BYTE)
                            self.debug('writing {} ({}) into mem at address' \
                                ' 0x{:08x}'.format(bin_val, repr(char), data_addr))
                            self.mem_write(data_addr, bin_val)
                            data_addr += 1
                        data_addr -= 1
                    elif directive == '.space':
                        self.local_symbols[f][label] = data_addr
                        val = values[0]
                        self.debug('reserving {} bytes for {} starting at' \
                            ' 0x{:08x}'.format(val, label, data_addr))
                        for _ in range(int(val)):
                            self.mem_write(data_addr, int2bin(0, bits=BYTE))
                            data_addr += 1        
        return instructions
           

    def _step(self):
        # Get instruction at PC
        instr = Instruction(self.instr_memory[self.PC])

if __name__ == '__main__':
    sim = SingleCycleSimulator(verbose=2)
    #sim.load_asm('test.asm')
    sim.print_reg(radix=int)
        