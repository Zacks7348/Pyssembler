from Pyssembler.errors import PyssemblerException
from enum import Enum


class AssemblerError(PyssemblerException):
    """
    This exception is thrown when an error occurs during
    program assembly

    This inherits from :class:`PyssemblerException`
    """
    def __init__(self, filename='', linenum='', charnum='',
            message='Could not assemble instruction', ):
        error_message = 'Error found in file: {filename}({linenum},{charnum})\n\t {message}'
        
        super().__init__(error_message.format(filename=filename, 
                linenum=linenum, charnum=charnum, message=message))

class AssemblerWarning(PyssemblerException):
    """
    This exception is thrown when a warning occurs during
    program assembly and the setting Warnings are Errors
    is turned on

    This inherits from :class:`PyssemblerException`
    """
    def __init__(self, filename='', linenum='', charnum='',
            message='Could not assemble instruction', ):
        error_message = 'Warning: {filename}({linenum},{charnum})\n {message}'
        
        super().__init__(error_message.format(filename=filename, 
                linenum=linenum, charnum=charnum, message=message))

class TokenizationError(PyssemblerException):
    """
    This exception is thrown when an error occurs during
    statement tokenization

    This inherits from :class:`PyssemblerException`
    """

    ERROR_MESSAGE = 'Error occured during tokenization: {filename}({linenum},{charnum})\n\t {message}'

    def __init__(self, filename, linenum, charnum, message) -> None:
        super().__init__(TokenizationError.ERROR_MESSAGE.format(
            filename=filename, linenum=linenum, charnum=charnum, message=message))