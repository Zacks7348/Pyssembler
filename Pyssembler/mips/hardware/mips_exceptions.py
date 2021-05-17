from ..errors import SimulatorError

class MIPSException(SimulatorError):
    """
    Base exception type for all mips32 exceptions

    This inherits from :class:`SimulatorError`
    """
    def __init__(self, error_code, error_abbr):
        self.error_code = error_code
        self.error_abbr = error_abbr

class InterruptException(MIPSException):
    """
    Exception thrown when an interrupt is made
    """
    def __init__(self):
        super().__init__(0, 'INT')

class AddressLoadException(MIPSException):
    """
    Exception thrown when trying to read a value from an invalid address when simulating
    """
    def __init__(self):
        super().__init__(4, 'ADDRL')

class AddressStoreException(MIPSException):
    """
    Exception thrown when trying to write a value to an invalid address when simulating
    """
    def __init__(self):
        super().__init__(5, 'ADDRS')

class SYSCALLException(MIPSException):
    """
    Exception thrown when syscall instruction executed
    """
    def __init__(self):
        super().__init__(8, 'SYSCALL')

class BreakException(MIPSException):
    """
    Exception thrown when break instruction executed
    """
    def __init__(self):
        super().__init__(9, 'BKPT')

class ReservedInstructionException(MIPSException):
    """
    Exception thrown when instruction signals reserved instruction
    """
    def __init__(self):
        super().__init__(10, 'RI')

class ArithmeticOverflowException(MIPSException):
    """
    Exception thrown when overflow is caught
    """
    def __init__(self):
        super().__init__(12, 'OVF')