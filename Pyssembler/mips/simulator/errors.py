from Pyssembler.errors import PyssemblerException


class SimulatorError(PyssemblerException):
    """
    The base exception type for all mips32 simulation errors

    This inherits from :class:`PyssemblerException`
    """


class SimulationExitException(SimulatorError):
    """
    Basic Exception that causes the Simulator to exit
    """

    def __init__(self, result=None) -> None:
        self.result = str(result)
