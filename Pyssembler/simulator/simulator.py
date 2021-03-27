import json
import os.path
import ast

from .utils import clean_code
from .utils import Binary, Integer
from .utils import WORD, HWORD, BYTE, BIT
from .instruction import Instruction
from .hardware import Memory, RegisterFile
from .hardware.coprocessors import CP0
from Pyssembler.simulator import instruction
from .errors import *

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

        self.ENCODINGS_FILE = os.path.dirname(__file__)+'/encodings.json'
        self.REGISTERS_FILE = os.path.dirname(__file__)+'/registers.json'


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
                for line, line_num in self.a_code[f]:
                    print(line_num, line)

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

        for entry in instructions:
            print(entry)

        # Ready to assemble instructions
        self.__assemble(instructions)

    def __include(self) -> bool:
        """
        Function to handle any .include directives

        If a file in self.asm_files is found in a .include directive,
        that file is removed from asm_files since all code will now
        be in the current file

        Returns True if successful, otherwise False
        """
        included_files = []
        to_include = []
        for f in self.asm_files:
            # if file has been included in another file, skip
            # this file will be removed from asm_files later
            if f in included_files: continue
            for i, (line, line_num) in enumerate(self.a_code[f]):
                if not line.startswith('.include'):
                    continue
                include_filename = ' '.join(line.split()[1:])
                if include_filename == f:
                    # Case when .include is found with filename = current filename
                    raise CircularIncludeDirectiveError(f, line_num)
                try:
                    # Try to open file from include directive
                    with open(include_filename, 'r') as f_include:
                        # add code from filename to to_include
                        # ([code], i) i is index to add code into
                        to_include.append((clean_code(f_include.readlines()), i))
                except:
                    # Could not open file
                    raise IncludeDirectiveFileNotFoundError(f, line_num) 
                if not include_filename in included_files:
                    included_files.append(include_filename)

            for code, i in to_include:
                self.a_code[f] = self.a_code[f][:i] + code + self.a_code[f][i+1:]

        for f in included_files:
            # Remove any included files from asm_files
            if f in self.asm_files: self.asm_files.remove(f)
        return True

    def generate_symbols(self) -> None:
        """
        Generates symbol tables for assembly program
        Creates 1 global symbol table and local
        symbol tables for each file. Checks that syntax is correct
        for label declaration.

        Returns a list of MIPS assembly instructions with corresponding
        text memory addresses and filename.
        """
        sizes = {'.word': WORD, '.half': HWORD, '.byte': BYTE}
        data_addr = self.memory.data_base_addr
        extern_addr = self.memory.extern_base_addr
        in_data = False # Assume we are in text segment until .data read
        PC_offset = 0 # For assigning each instruction a memory location
        instructions = [] # list of mips assembly instructions and addr to be stored in
        for f in self.asm_files:
            self.local_symbols[f] = {}
            for line, line_num in self.a_code[f]:
                if line.startswith('.data'): in_data = True
                elif line.startswith('.text'): in_data = False
                elif line.startswith('.globl'):
                    label = line.split()[1]
                    if label in self.global_symbols:
                        # global label already defined
                        raise GlobalSymbolDefinedError(f, line_num, label)
                    if label in self.local_symbols[f]:
                        # label has been defined locally already
                        # move it to global table and remove from local table
                        self.global_symbols[label] = self.local_symbols[f][label]
                        del self.local_symbols[f][label]
                    # label has not been defined yet
                    else: self.global_symbols[label] = None
                elif line.startswith('.align'):
                    n = int(line.split()[1])
                    if not 0 <= n <= 2:
                        # Invalid .align value
                        raise InvalidAlignDirectiveError(f, line_num, n)
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
                        self.mem_write(extern_addr, Binary.from_int(0, bits=BYTE))
                        extern_addr += 1
                elif line.startswith('.'):
                    raise UnsupportedDirectiveError(f, line_num, line)
                
                elif not in_data:
                    # text section
                    # add tuple to instructions: (instr, addr, f, orig line number)
                    to_add = line
                    if ':' in line:
                        label = line.split()[0].replace(':', '')
                        to_add = ' '.join(line.split()[1:])
                        if self.global_symbols.get(label, False):
                            # label exists in global table and has already been resolved
                            raise GlobalSymbolDefinedError(f, line_num, label)
                        if self.local_symbols[f].get(label, False):
                            # label exists in local table and has already been resolved
                            raise LocalSymbolDefinedError(f, line_num, label)
                        if not self.global_symbols.get(label, True):
                            # label exists in global table but is unresolved
                            self.global_symbols[label] = self.rf.PC + PC_offset
                        else:
                            # label does not exist in global table, add it to local
                            self.local_symbols[f][label] = self.rf.PC + PC_offset
                    instructions.append((to_add, self.rf.PC + PC_offset, f, line_num))
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
                                raise InvalidDataTypeError(f, line_num, 
                                    message='Cannot store string as word. Must use .ascii or .asciiz')
                            val = val.replace(',', '')
                            if "'" in val: val = ord(val.replace("'", ''))
                            else: val = int(val)
                            bin_val = Binary.from_int(val, bits=sizes[directive])
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
                            bin_val = Binary.from_int(ord(char), bits=BYTE)
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
                            self.mem_write(data_addr, Binary.from_int(0, bits=BYTE))
                            data_addr += 1        
        return instructions
           
    def __assemble(self, program: list):
        """
        Helper function for assembling mips instructions into
        their binary encodings

        Also performs final syntax checks. See errors.py for more details
        about each exception thrown
        """

        # helper functions
        def encode_register(reg: str) -> str:
            """
            Helper function to encode register into binary

            Throws InvalidRegisterError if reg is not a valid register
            """
            reg = reg.replace(',', '')
            if not reg in REGISTERS:
                raise InvalidRegisterError(filename, line_num, reg)
            return Binary.from_int(REGISTERS[reg], bits=5)
        
        def encode_immediate(i: str, bits: int, signed=False) -> str:
            """
            Helper function to encode an immediate value

            Throws InvalidInstructionFormatError if cannot convert i to int
            """
            try:
                # try converting string to int
                i = int(i)
            except:
                # try converting hex string to int
                try:
                    i = int(i, 16)
                except:
                    # could not read immediate into an int
                    raise InvalidInstructionFormatError(filename, line_num, i)
            return Binary.from_int(i, bits=bits, signed=signed)
        
        def encode_offset(label, bits):
            """
            Helper function to encode the offset for branch instructions
            """
            if label in self.global_symbols:
                target = self.global_symbols[label]
            elif label in self.local_symbols[filename]:
                target = self.local_symbols[filename][label]
            else:
                # referenced label not defined in global or local symbol table
                raise InvalidLabelError(filename, line_num, label)
            return Binary.from_int(target - addr - 4, bits=bits, signed=True)

        with open(self.ENCODINGS_FILE, 'r') as f:
            ENCODINGS = json.load(f)
        with open(self.REGISTERS_FILE, 'r') as f:
            REGISTERS = json.load(f)

        for line, addr, filename, line_num in program:
            parsed = line.split()
            instr = parsed[0]
            rs = None
            rt = None
            rd = None
            i16_s = None
            i16_u = None
            i21_s = None
            i26_u = None
            base = None
            sa = None
            sel = None
            encoding = None
            if instr in ENCODINGS['CPU Load/Store']:
                # instr is a load/store
                # format: instr $rt i16_s(base)
                rt = encode_register(parsed[1]) 
                parsed_address = parsed[2].split('(')
                if len(parsed_address) != 2:
                    # invalid format: not i16_s(base)
                    raise InvalidInstructionFormatError(filename, line_num, parsed[2])
                i16_s = encode_immediate(parsed_address[0], 16, signed=True)
                parsed_address[1] = parsed_address[1].replace(')', '')
                base = encode_register(parsed_address[1])
                encoding = ENCODINGS['CPU Load/Store'][instr]
            
            elif instr in ENCODINGS['ALU i16']:
                # instr is an ALU instruction that encodes an immediate
                # format: instr rt, rs, [i16_s, i16_u]
                rt = encode_register(parsed[1])
                rs = encode_register(parsed[2])
                if instr == 'sltiu':
                    i16_u = encode_immediate(parsed[3], 16, signed=False)
                else:
                    i16_s = encode_immediate(parsed[3], 16, signed=True)
                encoding = ENCODINGS['ALU i16'][instr]
            
            elif instr in ENCODINGS['ALU 3-Op']:
                # instr is ALU instruction with 3 registers
                # format: instr rd, rs, rt
                rd = encode_register(parsed[1])
                rs = encode_register(parsed[2])
                rt = encode_register(parsed[3])
                encoding = ENCODINGS['ALU 3-Op'][instr]
            
            elif instr in ENCODINGS['ALU 2-Op']:
                # instr is ALU instruction with 2 registers
                # format: instr rd, rs
                rd = encode_register(parsed[1])
                rs = encode_register(parsed[2])
                encoding = ENCODINGS['ALU 2-Op'][instr]
            
            elif instr in ENCODINGS['Shift']:
                # instr is a shift instruction
                # format: instr rd, rt, sa OR instr rd, rt, rs
                rd = encode_register(parsed[1])
                rt = encode_register(parsed[2])
                if instr.endswith('v'):
                    # shift variable instruction
                    rs = encode_register(parsed[3])
                else:
                    # shift immediate instruction
                    sa = encode_immediate(parsed[3], 5)
                encoding = ENCODINGS['Shift'][instr]
            
            elif instr in ENCODINGS['Trap i16']:
                # instr is a trap instruction
                # format: instr, rs, i16_s
                rs = encode_register(parsed[1])
                if instr.endswith('u'): i16_u = encode_immediate(parsed[2], 16, signed=False)
                else: i16_s = encode_immediate(parsed[2], 16, signed=True)
                encoding = ENCODINGS['Trap i16'][instr]
            
            elif instr in ENCODINGS['CP Move']:
                # instr moves value in CP0 register into GPR
                # format: instr rt, rd OR  instr rt, rd, sel
                rt = encode_register(parsed[1])
                rd = encode_register(parsed[2])
                if len(parsed) == 4:
                    sel = encode_immediate(parsed[3], 3, signed=False)
                encoding = ENCODINGS['CP Move'][instr]
            
            elif instr in ENCODINGS['Jump']:
                # instr is j, jal, or jalr
                if instr == 'jalr':
                    if len(parsed) == 2:
                        rs = encode_register(parsed[1])
                        rd = Binary.from_int(31, bits=5)
                    elif len(parsed) == 3:
                        rd = encode_register(parsed[1])
                        rs = encode_register(parsed[2])
                    else:
                        raise InvalidInstructionFormatError(filename, line_num, line)
                else:
                    # instr is j or jal
                    self.warning('Deprecated function {}. Use bc or balc'.format(instr))
                    if parsed[1] in self.global_symbols:
                        i26_u = Binary.from_int(self.global_symbols[parsed[1]], bits=26)
                    elif parsed[1] in self.local_symbols[filename]:
                        i26_u = Binary.from_int(self.local_symbols[filename][parsed[1]], bits=26)
                    else:
                        raise InvalidLabelError(filename, line_num, parsed[1])
                encoding = ENCODINGS['Jump'][instr]

            elif instr in ENCODINGS['Indexed Jumps']:
                # instr is jic or jialc
                # format: instr rt, i16_s
                rt = encode_register(parsed[1])
                i16_s = encode_offset(parsed[2], 16)
                encoding = ENCODINGS['Indexed Jumps'][instr]
            
            elif instr in ENCODINGS['Unconditional Branch']:
                # instr is an unconditional branch instruction
                # format: instr i26_s
                i26_s = encode_offset(parsed[1], 26)
                encoding = ENCODINGS['Unconditional Branch'][instr]
            
            elif instr in ENCODINGS['Compact Branch Zero 21']:
                # instr is a compact branch comparing with zero and an offset of 21 bits
                # format: instr rt, i21_s
                rt = encode_register(parsed[1])
                i21_s = encode_offset(parsed[2], 21)
                encoding = ENCODINGS['Compact Branch Zero 21'][instr]
            
            elif instr in ENCODINGS['Compact Branch Zero 16']:
                # instr is a compact branch comparing with zero and an offset of 16 bits
                # format: instr rt, i16_s
                rt = encode_register(parsed[1])
                i16_s = encode_offset(parsed[2])
                encoding = ENCODINGS['Compact Branch Zero 16'][instr]
            
            elif instr in ENCODINGS['Branch 2-Reg']:
                # instr is a branch comparing 2 GPR values
                # format: instr rs, rt, i16_s
                rs = encode_register(parsed[1])
                rt = encode_register(parsed[2])
                i16_s = encode_offset(parsed[3])
                encoding = ENCODINGS['Branch 2-Reg'][instr]
            
            elif instr in ENCODINGS['Branch Zero']:
                # instr is a branch comparing a GPR value with zero
                # format: instr rs, i16_s
                rs = encode_register(parsed[1])
                i16_s = encode_offset(parsed[2])
                encoding = ENCODINGS['Branch Zero'][instr]

            elif instr in ENCODINGS['Static']:
                encoding = ENCODINGS['Static'][instr]
            
            else:
                #raise UnsupportedInstructionError(filename, line_num)
                continue
            binary_code = encoding.format(rs=rs, rt=rt, rd=rd, i16_s=i16_s, 
                i16_u=i16_u, base=base, sa=sa, i21_s=i21_s, i26_u=i26_u, sel=sel)
            print(binary_code, line)
            #self.debug('Writing instruction {} into memory at address {}'.format(binary_code, addr))
            #self.mem_write(addr, binary_code)

    def _step(self):
        # Get instruction at PC
        instr = Instruction(self.instr_memory[self.PC])

if __name__ == '__main__':
    sim = SingleCycleSimulator(verbose=2)
    #sim.load_asm('test.asm')
    sim.print_reg(radix=int)
        