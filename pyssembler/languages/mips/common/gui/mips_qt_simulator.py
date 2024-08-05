from textwrap import dedent

from ..architecture.cpu import MIPSCPU
from ..architecture.assembler_errors import MIPSAssemblerError
from ..architecture.mips_exceptions import MIPSException
from pyssembler.core.architecture.qt_simulator import PyssemblerQtSimulatorBase
from pyssembler.utils import numeric


class MIPSQtSimulator(PyssemblerQtSimulatorBase[MIPSCPU]):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _debugger(self):
        pass
