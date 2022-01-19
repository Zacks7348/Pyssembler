import logging

from PyQt5.QtCore import Qt, QRunnable, pyqtSlot, pyqtSignal, QObject, QThreadPool
from PyQt5.QtWidgets import (
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QSplitter)
from Pyssembler.mips.errors import TokenizationError

from Pyssembler.mips.hardware import GPR, CP0, memory
from Pyssembler.mips import Assembler, Simulator, MIPSProgram
from Pyssembler.mips import AssemblerError
from Pyssembler.mips.simulator import SimulationExitException

from .tables import DataSegmentTable, TextSegmentTable, RegisterTable

__LOGGER__ = logging.getLogger('Pyssembler.GUI')


class SimulationSignals(QObject):
    """
    Defines the signals available from the simulation thread
    """

    executed = pyqtSignal(int)  # Current PC
    gpr_written = pyqtSignal(int, int)
    cp0_written = pyqtSignal(int, int)
    mem_written = pyqtSignal()
    finished = pyqtSignal(str)


class SimulatorWindow(QWidget):
    def __init__(self, consoles) -> None:
        super().__init__()
        self.consoles = consoles
        self.__init_ui()
        self.assembler = Assembler()
        self.program = None
        self.threadpool = QThreadPool()

    def __init_ui(self):
        self.regs = RegisterTable(self)
        self.regs.load_registers()
        self.text = TextSegmentTable()
        self.mem = DataSegmentTable()

        self.main_tabs = QTabWidget(self)
        self.main_tabs.addTab(self.text, 'Text Segment')
        self.main_tabs.addTab(self.mem, 'Data Segment')

        splitter = QSplitter()
        splitter.setOrientation(Qt.Horizontal)
        splitter.addWidget(self.main_tabs)
        splitter.addWidget(self.regs)
        splitter.setSizes([500, 50])
        layout = QVBoxLayout()
        layout.addWidget(splitter)
        self.setLayout(layout)

    def init_sim_env(self, main, files=None) -> bool:
        """
        Initialize the simulation environment for the specified program.

        First assembles the program. If any errors occur then stop and
        log error in pyssembler console.

        Initialize sim object

        Return False on error and return True if successful
        """

        __LOGGER__.debug('Initializing simulation environment...')
        files = [] if not files else files
        __LOGGER__.debug('Creating MIPS32 program...')
        self.consoles.p_message('Assembling program...')
        self.program = MIPSProgram(files, main=main)
        try:
            __LOGGER__.debug('Assembling program...')
            self.assembler.assemble(self.program)
        except AssemblerError as e:
            # An error occured during assembly, log error
            __LOGGER__.debug('Error occured during assembly!')
            self.consoles.p_message(str(e))
            return False
        except TokenizationError as e:
            # An error occured during tokenization, log error
            __LOGGER__.debug('Error occured during tokenization!')
            self.consoles.p_message(str(e))
            return False
        self.consoles.p_message('Successfully assembled program!')
        self.text.load_program(self.program)
        self.mem.load_memory()
        return True

    def start_simulation(self):
        """
        Starts the Simulation thread
        """
        worker = SimulationWorker()
        worker.signals.executed.connect(self.text.highlight)
        worker.signals.mem_written.connect(self.mem.load_memory)
        self.threadpool.start(worker)


class SimulationWorker(QRunnable):
    """
    This class performs the simulation in another thread
    """

    def __init__(self):
        self.sim = Simulator()
        self.signals = SimulationSignals()

    @pyqtSlot()
    def run(self):
        """
        Runs the MIPS32 simulation
        """

        GPR.add_observer(self.__on_gpr_write)
        CP0.add_observer(self.__on_cp0_write)
        memory.add_observer(self.__on_mem_write)
        self.sim.start(step=True)

        while True:
            try:
                addr = self.sim.execute_instruction()
                self.signals.executed.emit(GPR.pc)
            except SimulationExitException as e:
                self.signals.finished.emit(e.result)
                break
        GPR.remove_observer(self.__on_gpr_write)
        CP0.remove_observer(self.__on_cp0_write)
        memory.remove_observer(self.__on_mem_write)

    def __on_gpr_write(self, addr: int, val: int):
        self.signals.gpr_written.emit((addr, val))

    def __on_cp0_write(self, addr: int, val: int):
        self.signals.cp0_written.emit((addr, val))

    def __on_mem_write(self, addr: int, val: int, size: int):
        self.signals.mem_written.emit((addr, val, size))


