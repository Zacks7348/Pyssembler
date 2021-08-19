from enum import Enum
from typing import Text
from string import ascii_letters, digits
import logging

from .mips_program import MIPSProgram
from .errors import *
from .instructions import instruction_set as instr_set
from .hardware.memory import MemorySize, MemoryConfig
from .hardware import memory, registers
from .directives import DirectiveInfo, Directives
from .tokenizer import Token, TokenType, tokenize_line, tokenize_program

LOGGER = logging.getLogger('PYSSEMBLER.ASSEMBLER')

class Segment(Enum):
    DATA = 0
    TEXT = 1
    KDATA = 2
    KTEXT = 3


class Assembler:

    def __init__(self) -> None:

        # Memory pointers
        self.text_write = None
        self.ktext_write = None
        self.data_write = None
        self.kdata_write = None
        self.extern_write = None

        # Assembler data
        self.verbose = 0
        self.program = None
        self.current_segment = None
        self.current_line = None
        self.text = []
        self.ktext = []
        self.data = []
        self.kdata = []
        self.segment_contents = {
            Segment.TEXT: self.text,
            Segment.KTEXT: self.ktext,
            Segment.DATA: self.data,
            Segment.KDATA: self.kdata
        }
        self.dir_sizes = {
            Directives.WORD: (MemorySize.WORD, MemorySize.WORD_LENGTH_BYTES),
            Directives.HALF: (MemorySize.HWORD, MemorySize.HWORD_LENGTH_BYTES),
            Directives.BYTE: (MemorySize.BYTE, MemorySize.BYTE_LENGTH_BYTES)
        }

        self.valid_symbol_chars = ascii_letters+digits+'-_'

        self.warnings = []

    def __prepare_for_assembly(self, program: MIPSProgram, text_offset: int = 0,
                               ktext_offset: int = 0, data_offset: int = 0,
                               kdata_offset: int = 0, extern_offset: int = 0) -> int:
        """
        Prepares the program for assembly.

        Iterates over each program statement and does the following:
        1. Builds a global symbol table and a local symbol table for
            each source file
        2. Ensures that all labels being defined are valid and don't
            already exists
        3. Assigns a memory address to each mips instruction in all
            text/ktext segments
        4. Each statement is able to explicitly store a label, so if we 
            find one we can remove it from its tokens list and move it to
            that attribute

        .globl directives are noted but not handled until after all statements 
        have been read and tokenized. This ensures that all local 
        tables are built before symbols are moved from local to global and avoids 
        dealing with declaring a global symbol before the symbol is defined. Globl
        directives are handled in the same order that they were found.

        Each statement (except segment declarations and globl directives) is added to
        a list depending on the current segment. This makes it easier to assemble
        the program in later steps
        """

        self.text_write = MemoryConfig.text_base_addr + text_offset
        self.ktext_write = MemoryConfig.ktext_base_addr + ktext_offset
        self.data_write = MemoryConfig.data_base_addr + data_offset
        self.kdata_write = MemoryConfig.kdata_base_addr + kdata_offset
        self.extern_write = MemoryConfig.extern_base_addr + extern_offset

        self.program = program
        self.current_segment = Segment.TEXT  # Assume we are in text segment
        globl_statements = []

        # Tokenize the program
        # This will raise a TokenizationError if something goes wrong,
        # let that error go up to caller
        LOGGER.debug('Tokenizing program...')
        tokenize_program(self.program)
        LOGGER.debug('Tokenization complete!')

        # Expand any pseudo instructions
        LOGGER.debug('Expanding pseudo instructions...')
        i = 0
        while i < len(program):
            line = program.get_line(i)
            if instr_set.is_pseudo_instruction(line):
                #import pdb; pdb.set_trace()
                expanded = instr_set.expand_pseudo_instruction(line)
                if not expanded:
                    raise AssemblerError(
                        filename=line.filename,
                        linenum=line.linenum,
                        charnum=line.tokens[0].charnum,
                        message='Could not expand pseudo instruction'
                    )
                num_instr = len(expanded)
                expanded_tokens = []
                for exp in expanded:
                    expanded_tokens.append(tokenize_line(exp, line.filename, line.linenum))
                program.replace_pseudo_instruction(line, expanded, expanded_tokens)
                i += num_instr
                continue
            i += 1
        LOGGER.debug('Expanded all pseudo instructions!')

        LOGGER.debug('Generating symbol tables...')
        for line in self.program:
            self.current_line = line

            if line.tokens[0].type == TokenType.DIRECTIVE:
                # Statement starts with a directive
                # if statement declares new segment or is .globl, continue
                # so that this statement doesn't get added to
                # our segment lists
                if line.tokens[0].value == Directives.DATA:
                    self.current_segment = Segment.DATA
                    continue
                elif line.tokens[0].value == Directives.KDATA:
                    self.current_segment = Segment.KDATA
                    continue
                elif line.tokens[0].value == Directives.TEXT:
                    self.current_segment = Segment.TEXT
                    continue
                elif line.tokens[0].value == Directives.KTEXT:
                    self.current_segment = Segment.KTEXT
                    continue
                elif line.tokens[0].value == Directives.GLOBL:
                    # We will deal with these statements later
                    globl_statements.append(line)
                    continue
                elif line.tokens[0].value == Directives.EXTERN:
                    self.__validate_token_type(line.tokens[1], TokenType.LABEL)
                    label_token = line.tokens[1]
                    self.__check_for_duplicate_symbol(
                        label_token, check_global=True)
                    self.program.global_symbols.add(label_token.value)
                elif line.tokens[0].value == Directives.SPACE:
                    self.__validate_token_type(line.tokens[1], TokenType.LABEL)
                    label_token = line.tokens[1]
                    self.__check_for_duplicate_symbol(label_token)
                    self.program.get_local_symbols(line).add(label_token.value)
            elif line.tokens[0].type == TokenType.MNEMONIC:
                # statement is a mips instruction, should only appear in
                # text or kernel text segment
                if not self.current_segment in (Segment.TEXT, Segment.KTEXT):
                    raise AssemblerError(
                        filename=line.filename,
                        linenum=line.linenum,
                        charnum=line.tokens[0].charnum,
                        message='Instructions can only be in TEXT or KERNEL TEXT segments'
                    )
                # We need to assign this instruction a memory address. We do this
                # now so that we can assign any line references by label an address
                if self.current_segment == Segment.TEXT:
                    line.memory_addr = self.text_write
                    self.text_write += MemorySize.WORD_LENGTH_BYTES
                else:
                    line.memory_addr = self.ktext_write
                    self.ktext_write += MemorySize.WORD_LENGTH_BYTES
            else:
                # Statements should only start with a directive or an instruction
                # mnemonic
                raise AssemblerError(
                    filename=line.filename,
                    linenum=line.linenum,
                    charnum=line.tokens[0].charnum,
                    message='Invalid syntax: Unknown directive/instruction'
                )
            if not line.label is None:
                # statement has a label that may be referenced by another line
                self.__check_for_duplicate_symbol(line.label)
                self.program.get_local_symbols(line).add(
                    line.label.value, line.memory_addr)
            self.segment_contents[self.current_segment].append(line)

        for line in globl_statements:
            # Now we deal with all globl directives found
            # in the same order that they were found
            for token in line.tokens[1:]:
                # .globl directives may have more than one label
                self.__validate_token_type(token, TokenType.LABEL)
                self.__check_for_duplicate_symbol(token, check_global=True)
                local_symbols = self.program.get_local_symbols(line)
                if local_symbols.has(token.value):
                    # symbol has already been defined locally, move it to
                    # global table and delete from local
                    self.program.global_symbols.add(
                        token.value, local_symbols.get(token.value))
                    local_symbols.delete(token.value)
                else:
                    # Label has not been defined yet, throw warning
                    self.warnings.append(
                        AssemblerWarning(
                            filename=line.filename,
                            linenum=line.linenum,
                            charnum=line.tokens[1].charnum,
                            message='Referenced label {} not defined'.format(token.value)))
        LOGGER.debug('Finished generating symbol tables!')


    def assemble(self, program: MIPSProgram, text_offset: int = 0,
                 ktext_offset: int = 0, data_offset: int = 0,
                 kdata_offset: int = 0, extern_offset: int = 0) -> int:
        """
        Assembles a program and writes it to memory

        First step is preparing the program for assembly. This includes 
        building all symbol tables, tokenizing each statement and categorizing
        them based on segment location

        Then each segment's contents are parsed and assembled. data/kdata segments
        are dealt with first so that references made by the text/ktext segments
        will already have a memory address

        Parameters
        ----------
        program : MIPSProgram
            The program to be assembled
        text_offset : int, optional
            The starting text address to write user instructions to (default=0)
        ktext_offset : int, optional
            The starting ktext address to write kernel instructions to (default=0)
        data_offset : int, optional
            The starting data address to write user data to (default=0)
        kdata_offset : int, optional
            The starting kdata address to write kernel data to (default=0)
        extern_offset : int, optional
            The starting data address to write data declared as external to (default=0)
        """

        LOGGER.debug('Preparing to assemble program...')
        self.__prepare_for_assembly(program, text_offset, ktext_offset, data_offset,
                                    kdata_offset, extern_offset)
        LOGGER.debug('Preparations complete!')
        print(self.program.global_symbols.table)
        for table in self.program.local_symbols.values():
            print(table.table)
        LOGGER.debug('Assembling program...')

        for segment_type in (Segment.DATA, Segment.TEXT):
            # Tuple ensures we write program data to memory first before
            # assembling the text segment
            self.current_segment = segment_type
            for line in self.segment_contents[self.current_segment]:
                self.current_line = line
                if line.tokens[0].type == TokenType.DIRECTIVE:
                    self.__handle_directive(line)
                elif line.tokens[0].type == TokenType.MNEMONIC:
                    self.__handle_instruction(line)
        LOGGER.debug('Successfully assembled program!')

    def __handle_instruction(self, line):
        """
        Each statement has an attribute for the original tokens and prepared tokens.

        Need to replace labels with immediate value and replace integers read as strings
        as actual ints
        """
        LOGGER.debug('Encoding instruction at {}({})...'.format(line.filename, line.linenum))
        encoding = instr_set.encode_instruction(line)
        if encoding is None:
            # Something went wrong, could not assemble instruction
            raise AssemblerError(
                filename=line.filename,
                linenum=line.linenum,
                charnum=line.tokens[0].charnum,
                message='Could not assemble instruction')
        line.binary_instr = encoding
        #memory.write(line.memory_addr, encoding, size=MemorySize.WORD)
        LOGGER.debug('Writing instruction to memory...')
        memory.write_instruction(line.memory_addr, encoding, line)
        LOGGER.debug('Done')

    def __handle_directive(self, line):
        """Helper function for dealing with directives that write values into memory

        Raises
        ------
        AssemblerError
            If a validation check fails or something goes wrong
        """

        if line.tokens[0].value == Directives.ALIGN:
            # Should only appear in data/kdata segment
            self.__validate_directive_segment(Segment.DATA, Segment.KDATA)
            self.__validate_num_tokens(line.tokens, token_cnt=2)
            if line.tokens[1].type != TokenType.IMMEDIATE:
                raise AssemblerError(
                    filename=line.src_file,
                    linenum=line.line_num,
                    charnum=line.tokens[1].charnum,
                    message='.align directive requires an integer between 0 and 2')
            if not 0 <= line.tokens[1].value <= 2:
                raise AssemblerError(
                    filename=line.src_file,
                    linenum=line.line_num,
                    charnum=line.tokens[1].charnum,
                    message='.align directive requires an integer between 0 and 2')
            alignment = self.data_write % 2**line.tokens[1].value
            if alignment != 0:
                self.data_write += 2**line.tokens[1].value - alignment
        elif line.tokens[0].value in (Directives.ASCII, Directives.ASCIIZ):
            # Should only appear in data/kdata segment
            self.__validate_directive_segment(Segment.DATA, Segment.KDATA)
            # Expect 2 tokens (line label has already been stripped)
            self.__validate_num_tokens(line.tokens, token_cnt=2)
            if not line.label is None:
                # This line has a label that has already been validated,
                # assign it the address that the ascii string will be written to
                self.program.get_local_symbols(line).assign_addr(
                    line.label.value, self.data_write)
            self.__validate_token_type(line.tokens[1], TokenType.ASCII)
            ascii_string = line.tokens[1].value
            if line.tokens[0].value == Directives.ASCIIZ:
                ascii_string += '\0'
            for char in ascii_string:
                memory.write(self.data_write, ord(char), size=MemorySize.BYTE)
                self.data_write += MemorySize.BYTE_LENGTH_BYTES
        elif line.tokens[0].value == Directives.EXTERN:
            self.__validate_num_tokens(line.tokens, token_cnt=3)
            self.__validate_token_type(line.tokens[1], TokenType.LABEL)
            label_token = line.tokens[1]
            self.__check_for_duplicate_symbol(label_token, check_global=True)
            self.program.global_symbols.add(label_token.value, self.extern_write)
            self.__validate_token_type(line.tokens[2], TokenType.IMMEDIATE)
            for _ in range(line.tokens[2].value):
                memory.write(self.extern_write, 0, size=MemorySize.BYTE)
                self.extern_write += MemorySize.BYTE_LENGTH_BYTES
        elif line.tokens[0].value == Directives.SPACE:
            # Should only appear in data/kdata segment
            self.__validate_directive_segment(Segment.DATA, Segment.KDATA)
            self.__validate_num_tokens(line.tokens, token_cnt=2)
            self.__validate_token_type(line.tokens[1], TokenType.IMMEDIATE)
            if not line.label is None:
                self.program.get_local_symbols(line).add(
                    line.label.value, self.data_write)
            for _ in range(line.tokens[1].value):
                memory.write(self.data_write, 0, size=MemorySize.BYTE)
                self.data_write += MemorySize.BYTE_LENGTH_BYTES
        elif line.tokens[0].value in (Directives.WORD, Directives.HALF,
                                           Directives.BYTE):
            # Should only appear in data/kdata segment
            self.__validate_directive_segment(Segment.DATA, Segment.KDATA)
            self.__validate_num_tokens(line.tokens, min_tokens=2)
            if not line.label is None:
                # label has already been validated when stripped
                self.program.get_local_symbols(line).assign_addr(
                    line.label.value, self.data_write)
            for token in line.tokens[1:]:
                self.__validate_token_type(token, TokenType.IMMEDIATE)
                memory.write(self.data_write, token.value,
                    size=self.dir_sizes[line.tokens[0].value][0])
                self.data_write += self.dir_sizes[line.tokens[0].value][1]


    def __check_for_duplicate_symbol(self, token: Token, check_global : bool=False):
        """Util function for checking if a symbol is already defined

        Parameters
        ----------
        symbol : :class:`Token`
            the symbol to test
        check_global : :class:`bool`
            If true, search global symbol table instead of local

        Raises 
        ------
        AssemblerError 
            If symbol exists
        """

        if check_global:
            if self.program.global_symbols.has(token.value):
                # Symbol is already defined globally
                raise AssemblerError(
                    filename=self.current_line.filename,
                    linenum=self.current_line.linenum,
                    charnum=token.charnum,
                    message='Global symbol {} already defined'.format(token.value))
            return
        if self.program.get_local_symbols(self.current_line).has(token.value):
            # Symbol is already defined locally
            raise AssemblerError(
                filename=self.current_line.filename,
                linenum=self.current_line.linenum,
                charnum=token.charnum,
                message='Local symbol {} already defined'.format(token.value))

    def __validate_token_type(self, token: Token, type_: TokenType):
        """Helper function for validating a token's type

        Parameters
        ----------
        token : :class:`Token`
            The token to test
        type_ : :class:`TokenType`
            The type that token should be

        Raises
        ------
        AssemblerError
            If the type of token does not match type_
        """
        if not token.type == type_:
            raise AssemblerError(
                filename=self.current_line.filename,
                linenum=self.current_line.linenum,
                charnum=token.charnum,
                message='Invalid syntax')

    def __validate_directive_segment(self, *allowed_segments):
        """Util function for checking if a directive is in the right segment

        Parameters
        ----------
        allowed_segments : :class:`list`
            A list of valid segments to be in at this point

        Raises
        ------
        AssemblerError
            If validation fails
        """

        if not self.current_segment in allowed_segments:
            raise AssemblerError(
                filename=self.current_line.filename,
                linenum=self.current_line.linenum,
                charnum=self.current_line.tokens[0].charnum,
                message='{} directive can only appear in {} segments'.format(
                    self.current_line.tokens[0],
                    '/'.join(allowed_segments)
                )
            )

    def __validate_num_tokens(self, tokens, token_cnt=None, min_tokens=None):
        if not token_cnt is None:
            if len(tokens) != token_cnt:
                raise AssemblerError(
                    filename=self.current_line.filename,
                    linenum=self.current_line.linenum,
                    charnum=self.current_line.tokens[0].charnum,
                    message='{} directive should be formatted as: {}'.format(
                        tokens[0].value, Directives.get_format(tokens[0].value)
                    )
                )
        if not min_tokens is None:
            if len(tokens) < min_tokens:
                raise AssemblerError(
                    filename=self.current_line.filename,
                    linenum=self.current_line.linenum,
                    charnum=self.current_line.tokens[0].charnum,
                    message='{} directive should be formatted as: {}'.format(
                        tokens[0].value, Directives.get_format(tokens[0].value)
                    )
                )
