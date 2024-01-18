from __future__ import annotations
import typing

from pyssembler.exceptions import PyssemblerException
from pyssembler.architecture.core.exceptions import AssemblerException

if typing.TYPE_CHECKING:
    from pyssembler.architecture.mips.common.mips_token import MIPSToken

__all__ = [
    'MIPSAssemblerError',
    'MIPSSyntaxError',
    'MIPSInvalidSegmentError',
    'MIPSSymbolAlreadyExistsError',
    'MIPSIncludeError'
]


class MIPSAssemblerError(AssemblerException):
    def __init__(self, token: MIPSToken, summary='Invalid syntax'):
        """
        Initialize a MIPSAssemblerError
        :param token: The token that caused/was being processed when the error occured
        :param summary: Summary of what went wrong
        """
        error_msg = (f'Error occurred during assembly: '
                     f'{token.src.asm_file}({token.src.line_num},{token.src.line_char})\n\t{summary}')
        super().__init__(error_msg)
        self.token: MIPSToken = token
        self.summary: str = summary
        self.error_msg = error_msg


class MIPSSyntaxError(MIPSAssemblerError):
    """
    Base exception for AssemblerError exceptions raised due to syntax errors
    """
    pass


class MIPSInvalidSegmentError(MIPSAssemblerError):
    """TODO"""

    def __init__(self, token: MIPSToken):
        super().__init__(token, summary='Statement encountered in invalid segment!')


class MIPSSymbolAlreadyExistsError(MIPSAssemblerError):
    def __init__(self, symbol: MIPSToken):
        super().__init__(symbol, summary='Symbol already defined!')


class MIPSSymbolDoesNotExist(MIPSAssemblerError):
    def __init__(self, symbol: MIPSToken):
        super().__init__(symbol, summary='Undefined symbol!')


class MIPSIncludeError(MIPSAssemblerError):
    def __init__(self, token: MIPSToken, reason: str):
        super().__init__(token, summary=f'Could not include "{token.value}": {reason}')


class MIPSUnexpectedTokenError(MIPSAssemblerError):
    def __init__(self, token: MIPSToken, expected: MIPSToken):
        super().__init__(
            token,
            summary=f'Expected {expected.type.name}: Got {token.type.name}')
