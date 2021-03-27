from Pyssembler.errors import PyssemblerException

class AssembleError(PyssemblerException):
    """
    The base exception type for all assembly-related errors

    This inherits from :class:`PyssemblerException`
    """
    def __init__(self, filename, line_num, error='AssembleError',
            message='Could not assemble instruction',):
        error_message = 'File: {filename}\n  {error}({line_num}): {message}'
        
        super().__init__(error_message.format(filename=filename, 
                error=error, line_num=line_num, message=message))

class DirectiveError(AssembleError):
    """
    The base exception type for all directive-related assembling errors

    This inherits from :class:`AssembleError`
    """

class InstructionError(AssembleError):
    """
    The base exception type for all instruction-related assembling errors

    This inherits from :class:`AssembleError`
    """

class CircularIncludeDirectiveError(DirectiveError):
    """
    Exception that is thrown when a file has a .include directive
    that tries to include itself

    This inherits from :class:`DirectiveError`
    """
    def __init__(self, filename, line_num):
        message = 'Circular .include directive detected'
        super().__init__(filename, line_num, error=self.__class__.__name__, message=message)

class IncludeDirectiveFileNotFoundError(DirectiveError):
    """
    Exception that is thrown when attempting to open a file from a
    .include directive fails

    This inherits from :class:`DirectiveError` and is similar in nature
    to ``FileNotFoundError`` 
    """
    def __init__(self, filename, line_num):
        message = 'Could not open file from .include directive'
        super().__init__(filename, line_num, error=self.__class__.__name__, message=message)

class InvalidAlignDirectiveError(DirectiveError):
    """
    Exception that is thrown when a .align directive has an invalid value

    This inherits from :class:`DirectiveError`
    """
    def __init__(self, filename, line_num, value):
        message = 'Invalid alignment value {}. Must be 0, 1 or 2'.format(value)
        super().__init__(filename, line_num, error=self.__class__.__name__, message=message)

class UnsupportedDirectiveError(DirectiveError):
    """
    Directive that is thrown when a directive that is not supported is found

    This inherits from :class:`DirectiveError`
    """
    def __init__(self, filename, line_num, directive):
        message = 'Unsupported directive {}'.format(directive)
        super().__init__(filename, line_num, error=self.__class__.__name__, message=message)

class GlobalSymbolDefinedError(AssembleError):
    """
    Exception that is thrown when a file declares a symbol that has
    already been defined globally

    This inherits from :class:`AssembleError`
    """
    def __init__(self, filename, line_num, symbol):
        message = 'Global symbol {} already defined'.format(symbol)
        super().__init__(filename, line_num, error=self.__class__.__name__, message=message)

class LocalSymbolDefinedError(AssembleError):
    """
    Exception that is thrown when a file declares a symbol that has
    already been defined locally

    This inherits from :class:`AssembleError`
    """
    def __init__(self, filename, line_num, symbol):
        message = 'Local symbol {} already defined'.format(symbol)
        super().__init__(filename, line_num, error=self.__class__.__name__, message=message)

class InvalidDataTypeError(AssembleError):
    """
    Exception that is thrown when program tries to write a data value
    into memory in an invalid size format. IE storing a string as a .word

    This inherits from :class:`AssembleError`
    """
    def __init__(self, filename, line_num, message):
        super().__init__(filename, line_num, error=self.__class__.__name__, message=message)

class UnsupportedInstructionError(InstructionError):
    """
    Exception that is thrown when trying to assemble an unsupported instruction

    This inherits from :class:`InstructionError`
    """
    def __init__(self, filename, line_num):
        message = 'Unsupported Instruction'
        super().__init__(filename, line_num, error=self.__class__.__name__, message=message)

class InvalidInstructionFormatError(InstructionError):
    """
    Exception that is thrown when an instruction is not formatted
    properly

    This inherits from :class:`InstructionError`
    """
    def __init__(self, filename, line_num, malformed):
        message = 'Invalid format {}'.format(malformed)
        super().__init__(filename, line_num, error=self.__class__.__name__, message=message)

class InvalidRegisterError(InstructionError):
    """
    Exception that is thrown when an instruction being assembled has an 
    invalid register name.

    This inherits from :class:`InstructionError`
    """
    def __init__(self, filename, line_num, register):
        message = 'Invalid register '+register
        super().__init__(filename, line_num, error=self.__class__.__name__, message=message)

class InvalidLabelError(InstructionError):
    """
    Exception that is thrown when an instruction being assembled references
    an undefined label

    This inherits from :class:`InstructionError`
    """
    def __init__(self, filename, line_num, label):
        message = 'Undefined label {}'.format(label)
        super().__init__(filename, line_num, error=self.__class__.__name__, message=message)