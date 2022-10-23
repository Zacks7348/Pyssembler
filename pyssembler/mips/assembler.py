import logging
from typing import Any, Iterable, List, Union

from pyssembler.mips.tokens import Token, TokenType
from pyssembler.mips.errors import *
from pyssembler.mips.mips import Segment
from pyssembler.mips.directives import *
from pyssembler.mips.instructions import match_instruction
from pyssembler.mips.statement import MIPSStatement
from pyssembler.mips.symbol_table import SymbolTable


__LOGGER__ = logging.getLogger(__name__)


def generate_statements(
        lines: List[List[Token]],
        start_segment: Segment = Segment.TEXT):
    """
    Returns a list of cleaned list of tokenized statements.

    Cleaning includes:
    - removing whitespaces and comments
    - attaching labels to correct statements
    :param lines: The list of lines to clean
    :param start_segment: The segment the first line is in
    :return: Cleaned list of tokenized statements
    """
    __LOGGER__.debug(f'Generating statements from token list (starting at segment {start_segment.name})...')
    ignore = {TokenType.WHITESPACE, TokenType.COMMENT, TokenType.NEWLINE}
    statements = []
    unattached_label = None
    current_segment = start_segment
    segment_directives = {
        DATA_DIRECTIVE.name: Segment.DATA,
        KDATA_DIRECTIVE.name: Segment.KDATA,
        KTEXT_DIRECTIVE.name: Segment.KTEXT,
        TEXT_DIRECTIVE.name: Segment.TEXT}

    for line in lines:
        # Filter out whitespaces, comments, and newlines
        statement_tokens = [token for token in line if token.type not in ignore]
        if not statement_tokens:
            # Empty statement
            continue

        if statement_tokens[0].type == TokenType.LABEL:
            # First token of statement is a label, need to check to see if
            # the statement this label designates is this statement or a future
            # one. If the rest of the statement is not here, expect next
            # lines to be whitespaces or the statement
            label = statement_tokens[0]
            if len(statement_tokens) == 1:
                # Expected a colon after the label
                raise MIPSSyntaxError(
                    statement_tokens[0],
                    summary=f'Invalid Syntax: Expected :'
                )
            elif statement_tokens[1].type == TokenType.COLON:
                # Valid label definition, check if rest of statement
                # is here
                if len(statement_tokens) == 2:
                    # Designation is a statement located on a different
                    # line
                    unattached_label = label
                    continue
            else:
                raise MIPSSyntaxError(
                    statement_tokens[0],
                    summary=f'Invalid Syntax: Expected :'
                )
        statement = MIPSStatement(statement_tokens, current_segment, label=unattached_label)
        validate_statement(statement)
        # Check if statement is declaring a new segment
        if statement[0].value in segment_directives:
            current_segment = segment_directives[statement[0].value]
        statements.append(statement)

        if unattached_label is not None:
            unattached_label = None

    return statements


def build_symbol_tables(statements: List[MIPSStatement], global_table: SymbolTable):
    """
    Builds a global and local symbol table for the statements
    :return: The local symbol table
    """
    __LOGGER__.debug(f'Generating symbol tables...')
    local_table = SymbolTable()
    warnings = []

    globl_directives = []
    for statement in statements:
        if statement.label is not None:
            # Statement is labeled, add it to local table
            # Check if already exists in local namespace
            __check_for_duplicate_symbol(statement.label, local_table)
            local_table.update(statement.label.value, statement.label.location)
        if statement[0].value == GLOBL_DIRECTIVE.name:
            # Handle these later. labels defined with this directive
            # should be defined locally and be moved to the global table
            globl_directives.append(statement)
        elif statement[0].value == EXTERN_DIRECTIVE.name:
            # Label is token #2
            # Check if already exists in local and global namespace
            __check_for_duplicate_symbol(statement[1], global_table, local_table)
            global_table.update(statement[1].value, statement[1].location)
        elif statement[0].value == SPACE_DIRECTIVE.name:
            # Label is token #2
            # Check if already exists in local namespace
            __check_for_duplicate_symbol(statement[1], local_table)
            local_table.update(statement[1].value, statement[1].location)

    for globl_directive in globl_directives:
        # Globl directives may have more than one label
        for label in globl_directive[1:]:
            # Check if already exists in global namespace
            __check_for_duplicate_symbol(label, global_table)
            if local_table.has(label.value):
                # Symbol defined in local namespace. Need to move it
                # to global namespace
                global_table.update(label.value, local_table.get_location(label.value))
                local_table.delete(label.value)
            else:
                # Label has not been defined yet
                warnings.append(
                    MIPSAssemblerWarning(
                        globl_directive[0],
                        f'Referenced label {label.value} not defined!'
                    ))

    return local_table, warnings


def __check_for_duplicate_symbol(symbol: Token, *tables: SymbolTable):
    for table in tables:
        if table.has(symbol.value):
            raise MIPSAssemblerError(
                symbol,
                summary=f'"{symbol.value} already defined at {table.get_location(symbol.value)}!"'
            )


def validate_token_type(token: Token, *types: TokenType):
    """
    Validate that a token matches a TokenType or a set of TokenTypes

    Assumes the token list has already been cleaned
    """
    if token.type not in types:
        raise MIPSSyntaxError(
            token,
            summary=f'Invalid Syntax: Expected one of argument types {[t.name for t in types]}, got {token.type.name}'
        )


def validate_token_value(token: Token, *values: Any):
    """
    Validate that a token has a specific value

    Assumes the token list has already been cleaned
    """
    if token.value not in values:
        raise MIPSSyntaxError(
            token,
            summary=f'Invalid Syntax: Directive expected one of argument values {values}, got {token.value}'
        )


def validate_segment(statement: MIPSStatement, *allowed_segments: Segment):
    """
    Validate that a directive is declared in a correct segment

    Assumes the token list has already been cleaned
    """
    if statement.segment not in allowed_segments:
        raise MIPSSyntaxError(
            statement[0],
            summary=f'Invalid Syntax: Directive declared in invalid segment {statement.segment}'
        )


def validate_directive_statement(statement: MIPSStatement):
    """
    Validate that a directive statement contains the correct
    number of tokens.

    :param statement: List of tokens to test
    """
    if statement[0].type != TokenType.DIRECTIVE:
        raise MIPSSyntaxError(
            statement[0],
            summary='Invalid Syntax: Expected directive'
        )

    directive = DIRECTIVES[statement[0].raw_text]
    validate_segment(statement, *directive.segments)

    i = 1  # Token list pointer (ignore directive token)
    j = 0  # Directive format token pointer
    k = 0  # nargs counter
    while i < len(statement.tokens):
        fmt_type, fmt_vals, fmt_nargs = directive.fmt_tokens[j]
        validate_token_type(statement[i], *fmt_type)
        if fmt_vals:
            validate_token_value(statement[i], *fmt_vals)
        if fmt_nargs == '+':
            i += 1
        else:
            k += 1
            if k == fmt_nargs:
                j += 1
            i += 1


def validate_instruction_statement(statement: MIPSStatement):
    """
    Validate the instruction statement
    :param statement: The statement to validate
    """
    if not statement[0].type == TokenType.MNEMONIC:
        raise MIPSSyntaxError(
            statement[0],
            summary='Invalid Syntax: Expected mnemonic'
        )

    validate_segment(statement, Segment.TEXT, Segment.KDATA)

    if not match_instruction(statement):
        raise MIPSSyntaxError(
            statement[0],
            summary=f'Invalid Syntax: Invalid syntax for instruction {statement[0].value}'
        )


def validate_statement(statement: MIPSStatement):
    """
    Validate the statement
    :param statement: The statement to validate
    """
    if statement.is_directive():
        validate_directive_statement(statement)
    elif statement.is_instruction():
        validate_instruction_statement(statement)
        pass

