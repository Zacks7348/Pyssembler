from __future__ import annotations
from pathlib import Path
import re
import string
import typing

from . import directives, assembler_errors
from .cpu import MIPSCPU
from .mips_enums import *
from .mips_token import MIPSToken
from .mips_program import MIPSProgram
from .statement import MIPSStatement, MIPSTokenizedStatement
from .symbol_table import MIPSSymbolTable
from .hardware.constants import MIPSMemorySize
from pyssembler.architecture.core.base import PyssemblerAssembler
from pyssembler.architecture.core.program import *
from pyssembler.architecture.utils import Source, numeric, str_utils


class MIPSAssemblerContext:
    def __init__(self, assembler: 'MIPSAssembler'):
        self.assembler: 'MIPSAssembler' = assembler
        self.current_segment: Segment = Segment.TEXT
        self.user_text_ptr: int = 0
        self.user_data_ptr: int = 0
        self.kernel_text_ptr: int = 0
        self.kernel_data_ptr: int = 0
        self.seen_files: typing.Set[Path] = set()
        self.statements: typing.List[MIPSStatement] = []
        self.update_memory: bool = False
        self.process_includes: bool = False

        self.globl_symbols: MIPSSymbolTable = MIPSSymbolTable()
        self.file_symbols: typing.Dict[Path, MIPSSymbolTable] = {}
        self.global_symbol_list: typing.List[MIPSToken] = []

        self.warnings: typing.List = []

    def clear(self):
        self.seen_files.clear()
        self.statements.clear()
        self.globl_symbols.clear()
        self.file_symbols.clear()
        self.global_symbol_list.clear()
        self.warnings.clear()

    def get_file_symbol_table(self, f: Path):
        if f not in self.file_symbols:
            self.file_symbols[f] = MIPSSymbolTable()
        return self.file_symbols[f]

    def get_next_data_ptr(self, segment: Segment = None, reserved: int = 0):
        if segment is None:
            segment = self.current_segment

        if segment == Segment.DATA:
            ptr = self.user_data_ptr
            self.user_data_ptr += reserved

        elif segment == Segment.KDATA:
            ptr = self.kernel_data_ptr
            self.kernel_data_ptr += reserved

        else:
            raise RuntimeError(f'Segment must be one of {Segment.ANY_DATA}!')

        return ptr

    def get_next_text_ptr(self, segment: Segment = None, reserve: bool = False):
        if segment is None:
            segment = self.current_segment

        if segment == Segment.TEXT:
            ptr = self.user_text_ptr
            if reserve:
                self.user_text_ptr += MIPSMemorySize.WORD_LENGTH_BYTES

        elif segment == Segment.KTEXT:
            ptr = self.kernel_text_ptr
            if reserve:
                self.kernel_text_ptr += MIPSMemorySize.WORD_LENGTH_BYTES

        else:
            raise RuntimeError(f'Segment must be one of {Segment.ANY_TEXT}!')

        return ptr


class MIPSAssembler(PyssemblerAssembler[MIPSCPU]):
    """Represents the MIPS assembler"""

    # This regular expression is broken down as follows:
    # Alternative 1: \n (A single newline character)
    # Alternative 2: , (A single comma)
    # Alternative 3: : (A single colon)
    # Alternative 4: ( (A single left-parenthesis)
    # Alternative 5: ) (A single right-parenthesis)
    # Alternative 6: #.* (A sequence of non-newline chars starting with #)
    # Alternative 7: \s+ (A sequence of whitespace characters not including newlines)
    # Alternative 8: ".*" (A sequence of non-newline chars surrounded by double quotes)
    # Alternative 9: '.*' (A sequence of non-newline chars surrounded by single quotes)
    # Alternative 10: [^,:\(\)\s\"\']+ (A sequence of chars not found in the list)
    _MIPS_REGEX = re.compile(r'\n|,|:|\(|\)|#.*|\s+|\".*\"|\'.+\'|[^,:\(\)\s\"\']+')

    _ASCII_CHAR = '"'
    _COMMENT_CHAR = '#'
    _VALID_SYMBOL_CHARS = string.ascii_letters + string.digits + '_.$'
    _VALID_CHAR_SIZE = {3, 4}
    _SYMBOLS = {
        '\n': MIPSTokenType.NEWLINE,
        ',': MIPSTokenType.COMMA,
        ':': MIPSTokenType.COLON,
        '(': MIPSTokenType.LEFT_PARENTHESIS,
        ')': MIPSTokenType.RIGHT_PARENTHESIS
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._mnemonics: typing.Set[str] = set()
        self._directives: typing.List[directives.MIPSDirective] = []
        self._registers: typing.Set[str] = set()

        # Assembler Context
        self._ctx = MIPSAssemblerContext(self)

        self.__init_directives()

    @property
    def _directive_names(self):
        return {d.name for d in self._directives}

    def __init_directives(self):
        self._directives.append(directives.AlignDirective())
        self._directives.append(directives.AsciiDirective())
        self._directives.append(directives.AsciizDirective())
        self._directives.append(directives.ByteDirective())
        self._directives.append(directives.DataDirective())
        self._directives.append(directives.ExternDirective())
        self._directives.append(directives.GloblDirective())
        self._directives.append(directives.HalfDirective())
        self._directives.append(directives.IncludeDirective())
        self._directives.append(directives.KDataDirective())
        self._directives.append(directives.KTextDirective())
        self._directives.append(directives.SpaceDirective())
        self._directives.append(directives.TextDirective())
        self._directives.append(directives.WordDirective())

    def update(self):
        # Update set of valid instruction mnemonics
        self._mnemonics = self._cpu.instruction_set.get_all_mnemonics()
        self._registers = self._cpu.get_register_names()

    def assemble_program(
            self,
            program: MIPSProgram,
            user_text_ptr: int = None,
            user_data_ptr: int = None,
            kernel_text_ptr: int = None,
            kernel_data_ptr: int = None,
            update_memory: bool = True,
            process_includes: bool = True,
    ) -> None:
        # Initialize context
        self.update()
        self._ctx.clear()
        self._ctx.update_memory = update_memory
        self._ctx.process_includes = process_includes
        self._ctx.user_text_ptr = user_text_ptr
        self._ctx.user_data_ptr = user_data_ptr
        self._ctx.kernel_text_ptr = kernel_text_ptr
        self._ctx.kernel_data_ptr = kernel_data_ptr

        # Assemble files
        for asm_file in program.src_files:
            self._ctx.seen_files.add(asm_file.path)
            raw_statements = self.tokenize_text(
                asm_file.text(),
                asm_file=asm_file,
            )

            self.assemble_from_tokens(program, raw_statements)

        # TODO: Assemble exception handler

    def assemble_from_tokens(
            self,
            program: MIPSProgram,
            raw_statements: typing.List[MIPSTokenizedStatement],
            start_segment: Segment = Segment.TEXT,
    ) -> typing.List[MIPSStatement]:
        """Build a list of MIPS statements from a list of raw tokenized statements.

        MIPS is line oriented which means statements must appear on their
        own line. However, a label may appear on a previous line separated
        only by whitespace or comments.
        For example:

            > label: add $t1, $t2, $t3 # Comment

            > label:
            >
            > add $t1, $t2, $t3 # Comment

            > label:
            > # Comment
            > add $t1, $t2, $t3 # Comment

        All of the above raw statements will translate into the same MIPS statement:
            [label, add, $t1, $t2, $t3]
        """
        ignore = {MIPSTokenType.WHITESPACE, MIPSTokenType.COMMENT, MIPSTokenType.NEWLINE}
        unattached_label = None
        self._ctx.current_segment = start_segment

        for raw_statement in raw_statements:
            tokens = [t for t in raw_statement if t.type not in ignore]
            # Ignore empty statements
            if not tokens:
                continue

            if tokens[0].type == MIPSTokenType.LABEL:
                # First token of statement is a label, need to check to see if
                # the statement this label designates is this statement or a future
                # one. If the rest of the statement is not here, expect next
                # lines to be whitespaces or the statement
                label = tokens[0]
                if len(tokens) == 1:
                    # Expected a colon after the label
                    raise assembler_errors.MIPSSyntaxError(
                        tokens[0],
                        summary=f'Invalid Syntax: Expected :'
                    )

                elif tokens[1].type == MIPSTokenType.COLON:
                    # Valid label definition, check if rest of statement
                    # is here
                    unattached_label = label
                    if len(tokens) == 2:
                        # Designation is a statement located on a different
                        # line
                        continue

                    else:
                        # More tokens, expect rest of statement here
                        tokens = tokens[2:]

                else:
                    raise assembler_errors.MIPSSyntaxError(
                        tokens[0],
                        summary=f'Invalid Syntax: Expected :'
                    )

            statement = MIPSStatement(program, tokens, label=unattached_label, segment=self._ctx.current_segment)
            self._validate_statement(statement)

            # Execute any directives
            if statement.is_directive():
                statement.directive_impl.execute(statement, self._ctx, self._cpu)

            elif statement.is_instruction():
                # Assign a memory address
                statement.address = self._ctx.get_next_text_ptr(segment=statement.segment, reserve=True)

                # Update symbol table
                if statement.label is not None:
                    local_symbols = statement.program.get_file_symbols(statement.src.asm_file)
                    if local_symbols.has_symbol(statement.label.value):
                        raise assembler_errors.MIPSSymbolAlreadyExistsError(statement.label)
                    local_symbols.add_symbol(
                        statement.label.value,
                        source=statement.label.src,
                        address=statement.address
                    )

                self._ctx.statements.append(statement)

            unattached_label = None

        # Handle Globally declared symbols now that all local symbol tables
        # are constructed.
        for global_symbol in self._ctx.global_symbol_list:
            # Check if this symbol is already declared global
            if program.global_symbols.has_symbol(global_symbol.value):
                raise assembler_errors.MIPSSymbolAlreadyExistsError(global_symbol)

            # Check that this symbol was defined locally
            local_symbols = program.get_file_symbols(global_symbol.src.asm_file)
            if not local_symbols.has_symbol(global_symbol.value):
                raise assembler_errors.MIPSSymbolDoesNotExist(global_symbol)

            # Move from local symbol table into global
            symbol_item = local_symbols.get_symbol(global_symbol.value)
            local_symbols.remove_symbol(global_symbol.value)
            program.global_symbols.add_symbol(
                symbol_item.name,
                source=symbol_item.source,
                address=symbol_item.address
            )

        # Write instructions into memory.
        # All symbol tables should be fully populated at this point.
        if self._ctx.update_memory:
            for statement in self._ctx.statements:
                encoding = statement.instr_impl.assemble(statement)
                self._cpu.memory.write_instruction(statement.address, statement)
                self._cpu.memory.write_word(statement.address, encoding)

        statements = self._ctx.statements.copy()
        return statements

    def tokenize_text(self,
                      text: str,
                      line_start: int = 0,
                      char_start: int = 0,
                      asm_file: AssemblyFile = None,
                      ignore_whitespace: bool = True,
                      ignore_comments: bool = True,
                      custom_tokens: typing.Dict[str, MIPSTokenType] = None,
                      ) -> typing.List[MIPSTokenizedStatement]:
        """Tokenizes text into a list of raw MIPS Statements.

        :param text: The text to tokenize
        :param line_start: The starting line number to record for tokens
        :param char_start: The starting character number to record for tokens
        :param asm_file: Optional, The source file the text is from (default=None)
        :param ignore_whitespace: Optional, ignore any whitespace tokens (default=True)
        :param ignore_comments: Optional, ignore any comment tokens (default=True)
        :param custom_tokens: Optional, a mapping of custom token strings
                              to a token type (default=None).
        :return: A list of `TokenizedStatement`
        """
        self._log.debug(f'Tokenizing text...')
        token_list = []  # Temporary list of consumed tokens
        statements = []  # List of statements to return
        line_cnt = line_start  # Line counter
        line_char_cnt = 0  # Character counter relative to line
        char_cnt = char_start  # Character counter

        # Use regular expression to perform tokenization
        for raw_token in self._MIPS_REGEX.findall(text):
            src = Source(asm_file, line_cnt, line_char_cnt, char_cnt)
            processed_token = self._process_raw_token(raw_token, src, custom_tokens=custom_tokens)

            if ignore_whitespace and processed_token.type == MIPSTokenType.WHITESPACE:
                continue

            if ignore_comments and processed_token.type == MIPSTokenType.COMMENT:
                continue

            # Add processed token to statement
            token_list.append(processed_token)

            # Newlines indicate end of statement
            if processed_token.type == MIPSTokenType.NEWLINE:
                line_cnt += 1
                line_char_cnt = 0
                if token_list:
                    statements.append(MIPSTokenizedStatement(token_list))
                    token_list = []
            else:
                line_char_cnt += processed_token.length()

            char_cnt += processed_token.length()

        # Flush last statement incase no newline exists
        if token_list:
            statements.append(MIPSTokenizedStatement(token_list))

        return statements

    def _process_raw_token(
            self,
            raw_token: str,
            src: Source,
            custom_tokens: typing.Dict[str, MIPSTokenType] = None,
    ) -> MIPSToken:
        """Process a raw token.

        :param raw_token: The raw token to process.
        :param src: The source of the raw token.
        :param custom_tokens: Optional, a mapping of custom token strings
                              to a token type (default=None).
        :return: A `Token`.
        """
        token_type = MIPSTokenType.UNKNOWN
        token_value = raw_token

        # Check if the raw token matches any custom tokens
        if custom_tokens is not None:
            token_type = custom_tokens.get(raw_token, MIPSTokenType.UNKNOWN)
            if token_type != MIPSTokenType.UNKNOWN:
                return MIPSToken(token_type, raw_token, token_value, src)

        # Check if the raw token is a symbol
        if raw_token in self._SYMBOLS:
            token_type = self._SYMBOLS[raw_token]

        # Check if the raw token is whitespace (not including newlines)
        elif raw_token.isspace():
            token_type = MIPSTokenType.WHITESPACE

        # Check if the raw token is an ASCII string
        elif raw_token.startswith('"') and raw_token.endswith('"') and len(raw_token) > 1:
            token_type = MIPSTokenType.ASCII
            token_value = str_utils.process_escape_chars(raw_token[1:-1])

        # Check if the raw token is a char.
        # Characters can only be length 3 (or for if it is an escape char like '\n')
        elif raw_token.startswith('"') and raw_token.endswith('"') and len(raw_token) in (3, 4):
            token_type = MIPSTokenType.CHAR
            token_value = numeric.from_string(raw_token[1:-1])

        # Check if the raw token is a comment
        elif raw_token.startswith(self._COMMENT_CHAR):
            token_type = MIPSTokenType.COMMENT

        # Check if the raw token is a directive
        elif raw_token in self._directive_names:
            token_type = MIPSTokenType.DIRECTIVE

        # Check if the raw token is a mnemonic
        elif raw_token in self._mnemonics:
            token_type = MIPSTokenType.MNEMONIC

        # Check if the raw token is a register
        elif raw_token in self._registers:
            token_type = MIPSTokenType.REGISTER
            token_value = self._cpu.get_register_address(raw_token)

        # Check if the raw token is an immediate
        elif (i := numeric.from_string(raw_token)) is not None:
            token_type = MIPSTokenType.IMMEDIATE
            token_value = i

        # check if the raw token is a valid label
        elif self._is_valid_label(raw_token):
            token_type = MIPSTokenType.LABEL

        return MIPSToken(token_type, raw_token, token_value, src)

    def _is_valid_label(self, label: str) -> bool:
        """Returns True if the label is valid"""
        if not label:
            return False

        if not label[0].isalpha():
            return False

        for c in label[1:]:
            if c not in self._VALID_SYMBOL_CHARS:
                return False

        return True

    def _validate_statement(self, statement: MIPSStatement) -> None:
        # Check if this statement has a label which is already defined.
        if statement.label is not None:
            local_symbols = statement.program.get_file_symbols(statement.src.asm_file)
            if local_symbols.has_symbol(statement.label.value):
                raise assembler_errors.MIPSSymbolAlreadyExistsError(statement.label)

        if statement.is_directive():
            for directive in self._directives:
                # Try to match this statement to a known directive.
                # This will raise a MIPSSyntaxError if the statement
                # matches the directive but is not formatted properly.
                if directive.match(statement):
                    statement.directive_impl = directive
                    return

        elif statement.is_instruction():
            # Try to match against instruction
            instr = self._cpu.instruction_set.match_instruction(statement)
            statement.instr_impl = instr
