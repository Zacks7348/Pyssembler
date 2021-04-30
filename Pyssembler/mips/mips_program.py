from .errors import *
from .hardware import WORD, HWORD, BYTE, MEM, RF

import ast


class MIPSProgram:
    """
    Represents a mips program. 
    """

    def __init__(self, src_files: list = None, exception_handler: str = None) -> None:
        self._src_files = src_files
        self.exception_handler = exception_handler
        self._global_symbols = {}
        self._local_symbols = {}
        self.program = {}
        self.code = []

        self.load_files(self._src_files,
                        self.exception_handler)

    def load_files(self, src_files: list = None, exception_handler: str = None) -> None:
        """
        Read a list of asm files and parse input
        #TODO: handle exception handler files
        """
        if exception_handler:
            self.program[exception_handler] = self._read(exception_handler)
        if src_files:
            for src in src_files:
                self.program[src] = self._read(src)

    def prepare(self, PC_offset=0) -> None:
        """
        Prepares this mips program for assembly.

        Generates symbol tables and handles any directives in program.
        This function also performs some light syntax checking

        PC_offset is used to choose where the program starts being written to in mem
        PC_offset = 0: first instruction is written to MEM[text_base_addr]

        self.code is populated with tuples:
        (instr, filename, line_num, mem_addr)
        """
        self.code = [] # Reset list of prepared instructions
        self._include()
        sizes = {'.word': WORD, '.half': HWORD, '.byte': BYTE}
        data_addr = MEM.data_base_addr
        extern_addr = MEM.extern_base_addr
        in_data = False  # Assume we are in text segment until .data read
        for f in self._src_files:
            self._local_symbols[f] = {}
            for line, line_num in self.program[f]:
                if line.startswith('.data'):
                    in_data = True
                elif line.startswith('.text'):
                    in_data = False
                elif line.startswith('.globl'):
                    label = line.split()[1]
                    if label in self._global_symbols:
                        # global label already defined
                        raise GlobalSymbolDefinedError(f, line_num, label)
                    if label in self._local_symbols[f]:
                        # label has been defined locally already
                        # move it to global table and remove from local table
                        self._global_symbols[label] = self._local_symbols[f][label]
                        del self._local_symbols[f][label]
                    else:
                        # label has not been defined yet
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
                    self._global_symbols[label] = extern_addr
                    for _ in range(int(num_bytes)):
                        MEM.write(extern_addr, 0, size=BYTE)
                        extern_addr += 1

                elif not in_data:
                    # text section
                    # add tuple to instructions: (instr, addr, f, orig line number)
                    to_add = line
                    if ':' in line:
                        label = line.split()[0].replace(':', '')
                        to_add = ' '.join(line.split()[1:])
                        if self._global_symbols.get(label, False):
                            # label exists in global table and has already been resolved
                            raise GlobalSymbolDefinedError(f, line_num, label)
                        if self._local_symbols[f].get(label, False):
                            # label exists in local table and has already been resolved
                            raise LocalSymbolDefinedError(f, line_num, label)
                        if not self._global_symbols.get(label, True):
                            # label exists in global table but is unresolved
                            self._global_symbols[label] =  MEM.text_base_addr + PC_offset
                        else:
                            # label does not exist in global table, add it to local
                            self._local_symbols[f][label] =  MEM.text_base_addr + PC_offset
                    self.code.append((to_add, f, line_num,  MEM.text_base_addr + PC_offset))
                    PC_offset += 4

                else:
                    # in data segment
                    parsed = line.split()
                    label = parsed[0].replace(':', '')
                    directive = parsed[1]
                    values = parsed[2:]
                    if directive in sizes:
                        # .word, .half, or .byte directives
                        # determines alignment
                        align = (sizes[directive] // BYTE)
                        if data_addr % align != 0:
                            data_addr += align - (data_addr % align)
                        self._local_symbols[f][label] = data_addr
                        for val in values:
                            if '"' in val:
                                raise InvalidDataTypeError(f, line_num,
                                                           message='Cannot store string as word. Must use .ascii or .asciiz')
                            val = val.replace(',', '')
                            if "'" in val:
                                val = ord(val.replace("'", ''))
                            else:
                                val = int(val)
                            MEM.write(data_addr, val, size=sizes[directive])
                            data_addr += align
                    elif directive == '.ascii' or directive == '.asciiz':
                        self._local_symbols[f][label] = data_addr
                        string = ' '.join(values)
                        string = ast.literal_eval(string)
                        if directive.endswith('z'):
                            string += '\0'
                        for char in string:
                            val = ord(char)
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
                    elif line.startswith('.'):
                        raise UnsupportedDirectiveError(f, line_num, line)

    def _include(self):
        """
        Parses through program and handles any .include directivess

        If a file in self._src_files is found in a .include directive,
        that file is removed from asm_files since all code will now
        be in the current file

        Returns True if successful, otherwise False
        """
        included_files = []
        to_include = []
        for filename in self._src_files:
            if filename in included_files:
                # if file has been included in another file, skip
                # this file will be removed from asm_files later
                continue
            for i, (line, line_num) in enumerate(self.program[filename]):
                if not line.startswith('.include'):
                    continue
                include_filename = ' '.join(line.split()[1:])
                if include_filename == filename:
                    # Detected .include directive trying to include itself
                    raise CircularIncludeDirectiveError(filename, line_num)
                try:
                    # Try to open file from .include directive
                    with open(include_filename, 'r') as f_include:
                        # add code from filename to to_include
                        # ([code], i) i is index to add code into
                        to_include.append(self._read(f_include.readlines(), i))
                except:
                    # Could not open file
                    raise IncludeDirectiveFileNotFoundError(filename, line_num)
                if not include_filename in included_files:
                    included_files.append(include_filename)

            for code, i in to_include:
                # insert all included code into internal instruction list
                self.program[filename] = self.program[filename][:i] + \
                    code + self.program[filename][i+1:]

        for filename in included_files:
            # Remove any included files from internal file list
            if filename in self._src_files:
                self._src_files.remove(filename)

    def _read(self, src: str) -> list:
        """
        Internal function for reading an asm file.

        Comments are ignored and labels are moved to the same line 
        as it's instruction (if needed). Leading and trailing whitespaces
        are also ignored.
        """
        output = []  # list of tuples (line, original line number)
        to_add = ''
        code = open(src, 'r')
        for i, line in enumerate(code.readlines()):
            line = line.strip()
            if line.startswith('#') or line == '':
                continue
            if '#' in line:
                line = line.split('#', 1)[0].strip()
            if line.endswith(":"):
                to_add = line + " "
                continue
            to_add += line
            output.append((' '.join(to_add.split()), i+1))
            to_add = ''
        code.close()
        return output
