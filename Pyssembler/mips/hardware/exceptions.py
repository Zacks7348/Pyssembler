class MIPSExceptionCodes:
    INT = 0  # Interrupt
    ADDRL = 4  # Load from an illegal address
    ADDRS = 5  # Store to an illegal address
    IBUS = 6  # Bus error on instruction fetch
    DBUS = 7  # Bus error on data reference
    SYSCALL = 8  # syscall instruction executed
    BKPT = 9  # break instruction executed
    RI = 10  # Reserved instruction
    OVF = 12  # Arithmetic overflow
    TRAP = 13
    DIVIDE_BY_ZERO = 15


class MIPSException(Exception):
    """
    Base exception type for all MIPS32 exceptions
    """

    def __init__(self, message: str, exeception_type: int) -> None:
        self.message = message
        self.exception_type = exeception_type
        super().__init__(message)


class AddressErrorException(MIPSException):
    """
    MIPS Exception raised when an Address Error occurs
    """

    def __init__(self, message: str, exeception_type: int, addr: int) -> None:
        self.address = addr
        super().__init__(message, exeception_type)


class SyscallException(MIPSException):
    """
    MIPS Exception raised when a syscall instruction is executed
    """

    def __init__(self, code: int) -> None:
        self.code = code
        super().__init__('syscall instruction executed', MIPSExceptionCodes.SYSCALL)


class BreakException(MIPSException):
    """
    MIPS Exception raised when a break instruction is executed
    """

    def __init__(self) -> None:
        super().__init__('break instruction executed', MIPSExceptionCodes.BKPT)


class ReservedInstructionException(MIPSException):
    """
    MIPS Exception raised when an instruction is designated as a Reserved Instruction
    """

    def __init__(self) -> None:
        super().__init__('break instruction executed', MIPSExceptionCodes.RI)


class ArithmeticOverflowException(MIPSException):
    """
    MIPS Exception raised when an arithmetic operation causes an overflow
    """

    def __init__(self) -> None:
        super().__init__('break instruction executed', MIPSExceptionCodes.OVF)


class TrapException(MIPSException):
    """
    MIPS Exception raised when a trap instruction is true
    """

    def __init__(self) -> None:
        super().__init__('Trap raised', MIPSExceptionCodes.TRAP)


class DivideByZeroException(MIPSException):
    """
    MIPS Exception raised when a division by zero occurs
    """

    def __init__(self) -> None:
        super().__init__('Trap raised', MIPSExceptionCodes.DIVIDE_BY_ZERO)
