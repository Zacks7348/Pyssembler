from Pyssembler.errors import PyssemblerException

class SimulationException(PyssemblerException):
    """
    The base exception for all MIPS exceptions thrown during simulation
    """

class IntegerOverflow(SimulationException):
    """
    MIPS Exception raised when an integer overflow occurs
    """

class BreakpointException(SimulationException):
    """
    MIPS Exception raised when a BREAK occurs
    """

class AddressError(SimulationException):
    """
    MIPS Exception raised when an Address Error occurs
    """

class SystemCall(SimulationException):
    """
    MIPS Exception raised when a System Call occurs
    """

class Trap(SimulationException):
    """
    MIPS Exception raised when a Trap occurs
    """