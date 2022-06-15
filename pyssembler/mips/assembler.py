from enum import Enum
from typing import Any, Iterable, List, Union

from pyssembler.mips.tokenizer import TokenType, Token
from pyssembler.mips.errors import *
from pyssembler.mips.mips import Segment
from pyssembler.mips.directives import DIRECTIVES
from pyssembler.mips.instructions import match_instruction


def clean_lines(lines: List[List[Token]]):
    """
    Returns a list of cleaned list of tokenized statements.

    Cleaning includes:
    - removing whitespaces and comments
    - attaching labels to correct statements
    :param lines: The list of lines to clean
    :return: Cleaned list of tokenized statements
    """
    ignore = {TokenType.WHITESPACE, TokenType.COMMENT, TokenType.NEWLINE}
    statements = []
    unattached_label = False
    for line in lines:
        statement = []
        for token in line:
            if token.type in ignore:
                continue
            statement.append(token)
        if not statement:
            # Empty statement
            continue
        if statement[0].type == TokenType.LABEL:
            # First token of statement is a label, need to check to see if
            # the statement this label designates is this statement or a future
            # one. If the rest of the statement is not here, expect next
            # lines to be whitespaces or the statement
            if len(statement) == 1:
                # Expected a colon after the label
                raise MIPSSyntaxError(
                    statement[0],
                    summary=f'Invalid Syntax: Expected :'
                )
            elif statement[1].type == TokenType.COLON:
                # Valid label definition, check if rest of statement
                # is here
                if len(statement) == 2:
                    # Designation is a statement located on a different
                    # line
                    unattached_label = True
                statements.append(statement)
            else:
                raise MIPSSyntaxError(
                    statement[0],
                    summary=f'Invalid Syntax: Expected :'
                )

        elif unattached_label:
            # This statement is attached to a label previously defined
            statements[-1] += statement
            unattached_label = False
        else:
            statements.append(statement)
    return statements


def remove_label_from_statement(statement: List[Token]):
    """
    Return the statement with the label definition, if there is one, removed

    :param statement: The statement to remove label from
    :return: The statement without a label definition
    """
    if statement[0].type == TokenType.LABEL:
        return statement[2:]
    return statement


def validate_token_type(token: Token, *types: List[TokenType]):
    """
    Validate that a token matches a TokenType or a set of TokenTypes

    Assumes the token list has already been cleaned
    """
    a = 0
    if token.type not in types:
        raise MIPSSyntaxError(
            token,
            summary=f'Invalid Syntax: Expected one of argument types {types}, got {token.type}'
        )


def validate_token_value(token: Token, *values: List[Any]):
    """
    Validate that a token has a specific value

    Assumes the token list has already been cleaned
    """
    if token.value not in values:
        raise MIPSSyntaxError(
            token,
            summary=f'Invalid Syntax: Directive expected one of argument values {values}, got {token.value}'
        )


def validate_segment(token: Token, current_segment: Segment,
                     *allowed_segments: List[Segment]):
    """
    Validate that a directive is declared in a correct segment

    Assumes the token list has already been cleaned
    """
    if current_segment not in allowed_segments:
        raise MIPSSyntaxError(
            token,
            summary=f'Invalid Syntax: Directive declared in invalid segment {current_segment}'
        )


def validate_directive_statement(statement: List[Token]):
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
    i = 1  # Token list pointer (ignore directive token)
    j = 0  # Directive format token pointer
    k = 0  # nargs counter
    while i < len(statement):
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


def validate_instruction_statement(statement: List[Token]):
    """
    Validate the instruction statement
    :param statement: The statement to validate
    """
    if not statement[0].type == TokenType.MNEMONIC:
        raise MIPSSyntaxError(
            statement[0],
            summary='Invalid Syntax: Expected mnemonic'
        )
    if not match_instruction(statement):
        raise MIPSSyntaxError(
            statement[0],
            summary=f'Invalid Syntax: Invalid format for instruction {statement[0].value}'
        )


def validate_statement(statement: List[Token]):
    """
    Validate the statement
    :param statement: The statement to validate
    """
    statement = remove_label_from_statement(statement)
    if statement[0].type == TokenType.DIRECTIVE:
        validate_directive_statement(statement)
    elif statement[0].type == TokenType.MNEMONIC:
        #validate_instruction_statement(statement)
        pass

