"""
This file contains custom exceptions implemented by pyssembler
"""
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pyssembler.mips.tokens import Token


# ------------------------------------------------------------------------
# Custom Errors
# ------------------------------------------------------------------------
class MIPSAssemblerError(Exception):
    """
    Base exception for exceptions raised during assembly
    """

    def __init__(self, token: Token, summary='Invalid syntax'):
        """
        Initialize a MIPSAssemblerError
        :param token: The token that caused/was being processed when the error occured
        :param summary: Summary of what went wrong
        """
        error_msg = f'Error occured during assembly: {token.filename}({token.line},{token.line_char})\n\t{summary}'
        super().__init__(error_msg)
        self.token: Token = token
        self.summary: str = summary


class MIPSSyntaxError(MIPSAssemblerError):
    """
    Base exception for AssemblerError exceptions raised due to syntax errors
    """
    pass


# ------------------------------------------------------------------------
# Custom Warnings
# ------------------------------------------------------------------------
class MIPSAssemblerWarning(Warning):
    """
    Base exception for exceptions raised during assembly
    """

    def __init__(self, token: Token, summary='Invalid syntax'):
        error_msg = f'Warning: {token.filename}({token.line},{token.char})\n\t{summary}'
        super().__init__(error_msg)
        self.summary = summary


class MIPSSyntaxWarning(MIPSAssemblerWarning):
    """
    Base exception for AssemblerError exceptions raised due to syntax errors
    """
    pass
