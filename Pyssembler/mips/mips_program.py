"""
DOCUMENTATION TAKES A LOT OF TIME
"""

from Pyssembler.mips.tokenizer import Token


class SymbolTable:
    """
    Represents a symbol table
    """

    def __init__(self) -> None:
        self.table = {}

    def has(self, symbol: str) -> bool:
        """Check if symbol exists in table

        Parameters
        ----------
        symbol : :class:`str`
            The symbol to check for

        Returns
        -------
        bool
            True if symbol is in this table
        """

        return symbol in self.table

    def add(self, symbol: str, addr: int = None) -> None:
        """Add a symbol to the table

        Overwrites symbol if it already exists in this table

        Parameters
        ----------
        symbol : :class:`str`
            The symbol to add
        addr : :class:`int`, optional
            The address associated with the symbol (default=None)
        """

        self.table[symbol] = addr

    def assign_addr(self, symbol: str, addr: int) -> None:
        """Assign an address to a symbol if it exists in this table

        Parameters
        ----------
        symbol : :class:`str`
            The symbol to assign an address to
        addr : :class:`int`, optional
            The address to be assigned

        Raises
        ------
        :class:`ValueError`
            If symbol does not exist in this table        
        """

        if not self.has(symbol):
            raise ValueError("Symbol does not exist! ({})".format(symbol))
        self.table[symbol] = addr

    def delete(self, symbol: str) -> None:
        """If symbol exists in this table, delete it

        Parameters
        ----------
        symbol : :class:`str`
            The symbol to be deleted       
        """

        if symbol in self.table:
            del self.table[symbol]

    def get(self, symbol: str) -> int:
        """Get address of symbol if it exists in table

        Parameters
        ----------
        symbol : :class:`str`
            The symbol to get address of

        Returns
        :class:`int`
            The address of the symbol

        Raises
        ------
        :class:`ValueError`
            If symbol does not exist in this table
        """

        if not self.has(symbol):
            raise ValueError("Symbol does not exist! ({})".format(symbol))
        return self.table[symbol]

    def clear(self) -> None:
        """
        Clear this table of all entries
        """

        self.table.clear()


class SourceLine:
    """
    Represents an original line from a .asm file
    """

    def __init__(self, line: str, src_file: str, linenum: int) -> None:
        """
        Parameters
        ----------
        line : :class:`str`
            The original line read from a file
        src_file : :class:`str`
            The name of the file that line came from
        linenum : :class:`int`
            The line number of line
        """

        self.line = line
        self.src_file = src_file
        self.linenum = linenum


    def __str__(self):
        return 'SourceLine(line={})'.format(repr(self.line))


class ProgramLine:
    """
    Represents a single line in a mips program
    """

    def __init__(self, program: 'MIPSProgram', source: SourceLine,
                 memory_addr: int = None, tokens: list = None, label: Token = None) -> None:
        """
        Parameters
        ----------
        program : :class:`MipsProgram`
            The program that this line belongs to
        source : :class:`SourceLine`
            The SourceLine object that this line was created from. This allows
            this line to have access to both machine, assembly, and original lines
        memory_addr : :class:`int`, optional
            The address in simulated memory that this instruction is written to
        tokens : :class:`list`, optional
            The list of tokens generated by tokenizing the SourceLine
        label : :class:`Token`, None:
            The label found for referencing the address of this line
        """

        self.program = program
        self.source = source
        self.binary_instr = None
        self.memory_addr = memory_addr
        self.tokens = tokens
        self.operands = []
        self.label = label
        self.source_line = self.source.line
        self.clean_line = ' '.join(self.source_line.split()).split('#')[0]

    @property
    def filename(self):
        """
        Shortcut for getting filename of this line
        """
        return self.source.src_file

    @property
    def linenum(self):
        """
        Shortcut for getting linenum of this line
        """
        return self.source.linenum

    @property
    def src_line(self):
        return self.source.line
    
    @property
    def assembly(self):
        return ' '.join([str(token.src_val) for token in self.tokens])

    def __str__(self) -> str:
        return 'ProgramStatement(file={}, source={})'.format(
            self.filename, repr(self.source_line))
    def __repr__(self) -> str:
        return 'ProgramStatement(file={}, source={}, label={})'.format(
            self.filename, repr(self.source_line), self.label)


class MIPSProgram:
    """
    Represents a mips program.

    This class is responsible for storing the different levels of a
    mips program (original lines, tokenized statements, binary instructions)
    """

    def __init__(self, src_files: list = None, main: str = None) -> None:
        """
        Parameters
        ----------
        src_files : :class:`list`, optional
            A list of filenames to read into this program
        main : :class:`str`, optional
            A file that should be assembled first
        """
        self._src_files = src_files
        self.global_symbols = SymbolTable()
        self.local_symbols = {}

        self.program_lines = []
        self.src_lines = []

        self.load_files(self._src_files, main)

    def load_files(self, src_files: list = None, main: str = None) -> None:
        """Builds a list of :class:`SourceLine` objects by reading a list of asm files
        A file can be designated to be assembled first by passing it as main

        Each file that is read will have its own local symbol table created and can be
        accessed by :func:`.local_symbols[filename]`

        Parameters
        ----------
        src_files : :class:`list`, optional
            A list of filenames to read into this program
        main : :class:`str`, optional
            A file that should be assembled first
        """
        self.global_symbols.clear()
        self.local_symbols.clear()
        if main:
            self.local_symbols[main] = SymbolTable()
            self._read(main)
        if src_files:
            for src in src_files:
                self.local_symbols[src] = SymbolTable()
                self._read(src)

    def create_program_line_from_source(self, source: SourceLine, tokens: list, label: Token):
        """Create a :class:`ProgramLine` object from a :class:`SourceLine`

        Creates a :class:`ProgramLine` object and adds it to program_lines list

        Parameters
        ----------
        source : :class:`SourceLine`
            the SourceLine object to create from
        tokens : :class:`list`
            A list of tokens generated by a tokenizer
        label : :class:`Token`
            A token that represents a label that can be used to reference this line
        """

        self.program_lines.append(ProgramLine(self, source, tokens=tokens, label=label))

    def get_line(self, i: int) -> ProgramLine:
        """
        Get the program line at a specific address
        """

        try:
            return self.program_lines[i]
        except:
            return None
    
    def replace_pseudo_instruction(self, line: ProgramLine, replacements: list, new_tokens: list):
        """
        Replace the line with expanded instructions
        """
        for i in range(len(replacements)):
            tmp = ProgramLine(self, line.source, tokens=new_tokens[i], label=line.label)
            tmp.source_line = replacements[i]
            replacements[i] = tmp
        i = self.program_lines.index(line)
        self.program_lines = self.program_lines[:i] + replacements + self.program_lines[i+1:]

    def get_local_symbols(self, line: ProgramLine) -> SymbolTable:
        """Shortcut for getting local symbol table for a statement

        Returns None if table doesn't exist

        Parameters
        ----------

        """
        return self.local_symbols.get(line.filename, None)

    def _read(self, src: str) -> list:
        """Internal function for reading an asm file.

        The file is read line by line and each line is stored 
        in src_lines as a SourceLine object. This gives the program
        the ability to reference the original line contents
        """

        code = open(src, 'r')
        for i, line in enumerate(code.readlines(), start=1):
            self.src_lines.append(SourceLine(line, src, i))
        code.close()
    
    def __len__(self):
        return len(self.program_lines)

    def __iter__(self):
        """Shortcut for iterating over all ProgramLines
        Returns an interator object to iterate over all ProgramLines
        """
        return iter(self.program_lines)
