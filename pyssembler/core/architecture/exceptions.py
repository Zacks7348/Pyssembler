from pyssembler.exceptions import PyssemblerException


class AssemblerException(PyssemblerException):
    """Base Exception for all Assembler-related exceptions"""


class TokenizationException(AssemblerException):
    """Base Exception for all tokenizer-related exceptions"""

    def __init__(self, msg: str):
        self.msg = f'An error occured while tokenizing: {msg}'
        super().__init__()


class ProgramException(PyssemblerException):
    """Base Exception for all simulated program exceptions"""

    def __init__(self, msg: str):
        self.msg = msg
        super().__init__(msg)


class ProgramStopped(ProgramException):
    """Raised when a program stops executing"""

    def __init__(self, reason: str):
        msg = f'Program stopped: {reason}'
        super().__init__(msg)


class ProgramDroppedOff(ProgramStopped):
    """Raise when a program drops off"""
    def __init__(self, addr: int):
        super().__init__(f'Program dropped off at address 0x{addr:08x}')


class ProgramCrashed(ProgramException):
    """Raised when a program crashes during execution"""

    def __init__(self, reason: str):
        msg = f'Program crashed: {reason}'
