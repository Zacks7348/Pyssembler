import json
from os import name
import os.path
import ast

from .utils import clean_code
from .utils import Binary, Integer
from .utils import WORD, HWORD, BYTE, BIT
from .hardware import MEM, RF, CP0
from .hardware import GP_REGS, CP0_REGS
from Pyssembler.simulator.instruction import InstructionSet
from .errors import *


class Simulator:
    """
    Base Class for MIPS32 Simulators

    Provides all core components of a MIPS simulator. Also provides a function
    to assemble mips instructions
    """

    def __init__(self, step=False, debug_mode=False, prefix='[Simulator]') -> None:

        self.ENCODINGS_FILE = os.path.dirname(__file__)+'/encodings.json'

        # If step=True, wait for user input before executing next instr
        self.step = step
        self.debug_mode = debug_mode
        self.verbose_prefix = prefix

        # Load Instruction-Set
        self.instr_set = InstructionSet()
        self.instr_set.populate()

        # Simulation Modes
        self.SINGLE_INSTRUCTION = 0
        self.DELAY_SLOT = 1

        RF.write('PC', MEM.text_base_addr)

    def assemble(self, asm_files: list) -> None:
        self.debug('Assembling files...')
        self.global_symbols = {}
        self.local_symbols = {}
        self.asm_files = asm_files
        self.m_code = []  # machine code
        self.a_code = {}  # assembly code

        # Clean up asm files and store contents into a_code
        for f in self.asm_files:
            with open(f, 'r') as asm:
                self.a_code[f] = clean_code(asm.readlines())

        # Handle any .include directives
        self.__include()

        # Create symbol tables for program. also prepare memory
        # addresses for each instruction
        instructions = self.generate_symbols()

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
            if f in included_files:
                continue
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
                        to_include.append(
                            (clean_code(f_include.readlines()), i))
                except:
                    # Could not open file
                    raise IncludeDirectiveFileNotFoundError(f, line_num)
                if not include_filename in included_files:
                    included_files.append(include_filename)

            for code, i in to_include:
                self.a_code[f] = self.a_code[f][:i] + \
                    code + self.a_code[f][i+1:]

        for f in included_files:
            # Remove any included files from asm_files
            if f in self.asm_files:
                self.asm_files.remove(f)
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
        data_addr = MEM.data_base_addr
        extern_addr = MEM.extern_base_addr
        in_data = False  # Assume we are in text segment until .data read
        PC_offset = 0  # For assigning each instruction a memory location
        instructions = []  # list of mips assembly instructions and addr to be stored in
        for f in self.asm_files:
            self.local_symbols[f] = {}
            for line, line_num in self.a_code[f]:
                if line.startswith('.data'):
                    in_data = True
                elif line.startswith('.text'):
                    in_data = False
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
                    else:
                        self.global_symbols[label] = None
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
                    self.debug('Creating extern label {} at mem address'
                               ' {} of size {} bytes'.format(label, extern_addr, num_bytes))
                    for _ in range(int(num_bytes)):
                        MEM.write(extern_addr, 0, size=BYTE)
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
                            self.global_symbols[label] = RF.PC + PC_offset
                        else:
                            # label does not exist in global table, add it to local
                            self.local_symbols[f][label] = RF.PC + PC_offset
                    instructions.append(
                        (to_add, RF.PC + PC_offset, f, line_num))
                    PC_offset += 4  # PC + offset points to next empty address

                if not ':' in line:
                    continue
                parsed = line.split()
                if in_data:
                    # labels declared in .data section
                    label = parsed[0].replace(':', '')
                    directive = parsed[1]
                    values = parsed[2:]
                    if directive in sizes:
                        # .word, .half, or .byte directives
                        # determines alignment
                        align = (sizes[directive] // BYTE)
                        if data_addr % align != 0:
                            data_addr += align - (data_addr % align)
                        self.local_symbols[f][label] = data_addr
                        for val in values:
                            if '"' in val:
                                raise InvalidDataTypeError(f, line_num,
                                                           message='Cannot store string as word. Must use .ascii or .asciiz')
                            val = val.replace(',', '')
                            if "'" in val:
                                val = ord(val.replace("'", ''))
                            else:
                                val = int(val)
                            self.debug('writing {} into mem at address'
                                       ' {}'.format(val, data_addr))
                            MEM.write(
                                data_addr, val, size=sizes[directive])
                            data_addr += align

                    elif directive == '.ascii' or directive == '.asciiz':
                        self.local_symbols[f][label] = data_addr
                        string = ' '.join(values)
                        string = ast.literal_eval(string)
                        if directive.endswith('z'):
                            string += '\0'
                        for char in string:
                            val = ord(char)
                            self.debug('writing {} ({}) into mem at address'
                                       ' {}'.format(val, repr(char), data_addr))
                            MEM.write(data_addr, val, size=BYTE)
                            data_addr += 1
                    elif directive == '.space':
                        self.local_symbols[f][label] = data_addr
                        val = values[0]
                        self.debug('reserving {} bytes for {} starting at'
                                   ' {}'.format(val, label, data_addr))
                        for _ in range(int(val)):
                            MEM.write(data_addr, 0, size=BYTE)
                            data_addr += 1
        return instructions

    def __assemble(self, program: list):

        def encode_register(reg: str) -> str:
            """
            Helper function to encode a register
            Returns int addr of register or None if failed
            """
            reg = reg.replace(',', '')
            if reg in GP_REGS:
                return Binary.from_int(GP_REGS[reg], bits=5)
            if reg in CP0_REGS:
                return Binary.from_int(CP0_REGS[reg], bits=5)
            return None
        
        def encode_immediate(imm: str, bits: int, signed: bool) -> str:
            try:
                # Try to read offset as int
                return Binary.from_int(int(imm), bits=bits, signed=signed)
            except:
                try:
                    # Try to read offset as int from hex
                    return Binary.from_int(int(imm, 16), bits=bits, signed=signed)
                except:
                    return None

        def encode_target(target: str, filename, bits: int) -> str:
            if target in self.global_symbols:
                return Binary.from_int(self.global_symbols[target], bits=bits)
            if target in self.local_symbols[filename]:
                return Binary.from_int(self.local_symbols[filename][target], bits=bits)
            return None

        def encode_offset(label, filename, addr, bits):
            """
            Helper function to encode the offset for branch instructions
            """
            if label in self.global_symbols:
                return Binary.from_int(self.global_symbols[label] - addr - 4, bits=bits, signed=True)
            if label in self.local_symbols[filename]:
                return Binary.from_int(self.local_symbols[filename][label] - addr - 4, bits=bits, signed=True)
            return None

        for instr, addr, fname, line_num in program:
            tokens = instr.split() # split instruction by space
            instr_name = tokens[0] # first element should be instr name
            instr_info = self.instr_set.get_info(instr_name)
            if instr_info is None:
                # Instruction not found in instruction set
                raise UnsupportedInstructionError(fname, line_num)
            instr_format = instr_info['format'].split()
            if len(instr_format) != len(tokens):
                # Instruction doesn't match format
                raise InvalidInstructionFormatError(fname, line_num, instr_info)
            rt = None
            rs = None
            rd = None
            base = None
            offset = None
            immediate = None
            sa = None
            target = None
            for i, var in enumerate(instr_format[1:]):
                # loop through formatting of instruction to correctly
                # extract registers and immediates
                var = var.replace(',', '')
                if var == 'rt':
                    rt = encode_register(tokens[i+1])
                    if rt is None:
                        raise InvalidRegisterError(fname, line_num, tokens[i+1])
                
                elif var == 'rs':
                    rs = encode_register(tokens[i+1])
                    if rs is None:
                        raise InvalidRegisterError(fname, line_num, tokens[i+1])
                
                elif var == 'rd':
                    rd = encode_register(tokens[i+1])
                    if rd is None:
                        raise InvalidRegisterError(fname, line_num, tokens[i+1])

                elif var == 'offset(base)':
                    parsed = tokens[i+1].split('(')
                    base = parsed[1].replace(')', '')
                    base = encode_register(base)
                    if base is None:
                        raise InvalidRegisterError(fname, line_num, base)
                    offset = encode_immediate(parsed[0], instr_info['immediate length'], True)
                    if offset is None:
                        raise InvalidInstructionFormatError(fname, line_num, parsed[0])

                elif var == 'immediate':
                    immediate = encode_immediate(tokens[i+1], instr_info['immediate length'], True)
                    if immediate is None:
                        raise InvalidInstructionFormatError(fname, line_num, tokens[i+1])

                elif var == 'sa':
                    sa = encode_immediate(tokens[i+1], instr_info['immediate length'], False)
                    if sa is None:
                        raise InvalidInstructionFormatError(fname, line_num, tokens[i+1])

                elif var == 'target':
                    target = encode_target(tokens[i+1], fname, instr_info['immediate length'])
                    if target is None:
                        raise InvalidLabelError(fname, line_num, tokens[i+1])

                elif var == 'offset':
                    offset = encode_offset(tokens[i+1], fname, addr, instr_info['immediate length'])
                    if offset is None:
                        raise InvalidLabelError(fname, line_num, tokens[i+1]) 
            
            machine_instr = instr_info['encoding'].format(rt=rt, rs=rs, rd=rd, sa=sa, base=base, offset=offset, immediate=immediate, target=target)
            MEM.write(addr, int(machine_instr, 2), WORD)
            self.m_code.append(int(machine_instr, 2))
            self.debug('Wrote Instruction {} into mem[{}]'.format(machine_instr, addr))

    def simulate(self) -> None:
        cnt = 0
        while cnt < len(self.m_code):
            instruction = MEM.read_word(RF.PC)
            print(Binary.from_int(instruction), self.instr_set.instr_from_encoding(instruction))
            cnt += 1
            RF.increment_pc()
    
    def debug(self, message: str) -> None:
        if self.debug_mode:
            print('{}[DEBUG] {}'.format(self.verbose_prefix, message))

    def warning(self, message: str) -> None:
        print('{}[WARNING] {}'.format(self.verbose_prefix, message))

    def error(self, message: str) -> None:
        print('{}[ERROR] {}'.format(self.verbose_prefix, message))

    def bar(self) -> None:
        print('-'*50)

    def print_reg(self, radix=int):
        print('-------Registers-------')
        self.rf.print(radix)
        print('-----------------------')
