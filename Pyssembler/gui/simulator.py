import logging
from enum import Enum
import time

from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal, QThread, QObject
from PyQt5.QtWidgets import QTabWidget, QVBoxLayout, QWidget, QSplitter
from Pyssembler.mips.errors import TokenizationError

from Pyssembler.mips import Assembler, Simulator, MIPSProgram, AssemblerError
from Pyssembler.mips.simulator import ExitSimulation
from Pyssembler.mips.hardware import GPR, CP0

from .tables import DataSegmentTable, TextSegmentTable, RegisterTable

__LOGGER__ = logging.getLogger('Pyssembler.GUI')
__SIM_LOGGER__ = logging.getLogger('Pyssembler.SIM_THREAD')


class SimulatorWindow(QWidget):

    simulation_finished = pyqtSignal()
    simulation_started = pyqtSignal()

    def __init__(self, consoles) -> None:
        super().__init__()
        self.__sim_thread: QThread = None
        self.worker = None
        self.consoles = consoles
        self.__init_ui()
        self.assembler = Assembler()
        self.program = None
        self.__connected_slots = False

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
        self.consoles.p_message('Assembling program...\n')
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
            self.consoles.p_message(str(e)+'\n')
            return False
        self.consoles.p_message('Successfully assembled program!\n')
        self.text.load_program(self.program)
        self.mem.load_memory()
        return True

    def __start_simulation(self):
        """
        Starts the Simulation thread by emitting the play signal
        """

        __LOGGER__.info('Building simulation thread...')
        self.__sim_thread = QThread()
        self.__sim_thread.finished.connect(self.__thread_finished)

        __LOGGER__.info('Building simulation worker...')
        self.worker = SimulationWorker()

        self.worker.sim_finished.connect(self.__on_sim_finish)
        self.worker.sim_finished.connect(self.__sim_thread.deleteLater)
        self.worker.sim_finished.connect(self.__sim_thread.quit)
        self.worker.input_requested.connect(self.consoles.allow_mips_input)
        self.worker.output_requested.connect(self.consoles.m_message)
        self.worker.gpr_updated.connect(self.regs.gpr.update_register)
        self.worker.instr_fetched.connect(self.text.update_highlight)

        self.__sim_thread.started.connect(self.worker.run)
        self.__sim_thread.finished.connect(self.__sim_thread.deleteLater)
        self.consoles.input_recieved.connect(self.worker.send_input)

        __LOGGER__.info('Moving worker to simulation thread...')
        self.worker.moveToThread(self.__sim_thread)

        __LOGGER__.info('Starting simulation thread...')
        self.__sim_thread.start()

    def play_simulation(self):
        if not self.__sim_thread:
            self.__start_simulation()
        __LOGGER__.info('Starting simulation...')
        self.worker.play.emit()  # Play the simulation

    def stop_simulation(self):
        """
        Stops the Simulation thread
        """
        __LOGGER__.info('Stopping simulation thread...')
        self.worker.stop.emit()

    def pause_simulation(self):
        """
        Pause the running Simulation thread
        """
        __LOGGER__.info('Pausing simulation thread...')
        self.worker.pause.emit()

    def step_simulation_forward(self):
        """
        Execute only the next instruction in the Simulation
        """
        if not self.worker:
            # Sim thread has not started
            self.__start_simulation()
        __LOGGER__.info('Stepping forward in simulation thread...')
        self.worker.step_forward.emit()  # Step simulation forward

    def __on_sim_finish(self, result: str):
        self.consoles.p_message('\n')
        self.consoles.p_message(result)
        __LOGGER__.info(f'Simulation ended with result: {result}')
        self.simulation_finished.emit()

    def __thread_finished(self):
        __LOGGER__.info(f'Simulation thread finished, cleaning...')
        self.__sim_thread = None
        self.worker = None

    @property
    def is_thread_running(self):
        if not self.__sim_thread:
            return False
        return self.__sim_thread.isRunning()


class WorkerState(Enum):
    PLAY = 0
    STEP_FORWARD = 1
    STEP_BACKWARD = 2
    PAUSE = 3
    STOP = 4

        
class SimulationWorker(QObject):
    """
    Handles functionality of running the simulation

    This worker class is ran in a background thread (sim thread) by calling
    its moveToThread(QThread) function.

    Communication between the main thread and sim thread is done using Qt's
    signals. The worker uses the following signals to communicate progress with
    the simulation:

    executed - When an instruction has finished executing
    reg_updated - When a register was written to
    mem_updated - When a memory address has been written to
    sim_finished - When the simulation has finished
    input_requested - When user input is requested via a syscall,
                      see send_input()
    output_requested - When the simulation wants to output a string to console

    The following signals should be emitted to control the simulation:
    stop - Stops the simulation (eventually stops the sim thread)
    play - Plays the simulation
    pause - Pauses the simulation (without stopping the sim thread)
    step_forward - Plays the simulation for one step then pauses
    step_backward - NOT IMPLEMENTED, undos the simulation one step
    """
    
    # Status signals (only emitted by the worker)
    instr_fetched = pyqtSignal(int)  # PC address instruction fetched from
    gpr_updated = pyqtSignal(int, int)  # (address, value), address 32 is for PC
    mem_updated = pyqtSignal()
    sim_finished = pyqtSignal(str)
    input_requested = pyqtSignal()
    output_requested = pyqtSignal(str)

    # Control signals
    stop = pyqtSignal()
    play = pyqtSignal()
    pause = pyqtSignal()
    step_forward = pyqtSignal()
    step_backward = pyqtSignal()

    def __init__(self, delay: float = 0):
        super().__init__()
        self.sim = Simulator()
        self.sim.link_input_request_signal(self.input_requested)
        self.sim.link_output_request_signal(self.output_requested)

        self.state = None
        self.delay = delay

        self.play.connect(self.__play)
        self.stop.connect(self.__stop)
        self.pause.connect(self.__pause)
        self.step_forward.connect(self.__step_forward)
    
    @pyqtSlot()
    def run(self):
        """
        Starts the simulation
        """
        __SIM_LOGGER__.info('Running simulation...')
        self.__link_observers()
        self.sim.start(step=True)
        while True:
            time.sleep(self.delay)
            if self.state == WorkerState.STOP:
                break
            if self.state == WorkerState.PAUSE:
                # Stay here until state change
                __SIM_LOGGER__.info('Simulation paused')
                while self.state == WorkerState.PAUSE:
                    pass
                if self.state == WorkerState.STOP:
                    break
                __SIM_LOGGER__.info('Simulation resumed')
            if self.state in (WorkerState.PLAY, WorkerState.STEP_FORWARD):
                try:
                    self.sim.execute_instruction()
                except ExitSimulation as e:
                    # Program stopped executing
                    self.sim_finished.emit(e.result)
                    __SIM_LOGGER__.info('Program stopped executing, exiting sim thread...')
                    self.__unlink_observers()
                    return
                if self.state == WorkerState.STEP_FORWARD:
                    # Only execute one step then pause
                    self.state = WorkerState.PAUSE
        __SIM_LOGGER__.info('Simulation stopped')
        self.__unlink_observers()
        self.sim_finished.emit('Simulation stopped')

    # functions connected to control signals

    def __play(self):
        __SIM_LOGGER__.debug('PLAY signal recieved, playing simulation...')
        self.state = WorkerState.PLAY

    def __pause(self):
        __SIM_LOGGER__.debug('PAUSE signal recieved, stopping simulation...')
        self.state = WorkerState.PAUSE

    def __stop(self):
        __SIM_LOGGER__.debug('STOP signal recieved, stopping simulation...')
        self.state = WorkerState.STOP

    def __step_forward(self):
        __SIM_LOGGER__.debug('STEP_FORWARD signal recieved, stepping simulation...')
        self.state = WorkerState.STEP_FORWARD

    def __link_observers(self):
        GPR.add_observer(self.__on_gpr_update)
        self.sim.add_fetch_observer(self.__on_fetch)

    def __unlink_observers(self):
        GPR.remove_observer(self.__on_gpr_update)
        self.sim.remove_fetch_observer(self.__on_fetch)

    def __on_gpr_update(self, addr, val):
        __SIM_LOGGER__.debug(f'Detected GPR update: addr={addr}, val={val}, emitting signal...')
        self.gpr_updated.emit(addr, val)

    def __on_fetch(self, pc):
        __SIM_LOGGER__.debug(f'Instruction fetched at pc={pc}, emitting signal...')
        self.instr_fetched.emit(pc)

    # functions connected to io signals
    def send_input(self, message):
        __SIM_LOGGER__.debug('User input recieved, sending to simulator...')
        self.sim.send_input(message)

