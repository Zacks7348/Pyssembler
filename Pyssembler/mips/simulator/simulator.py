import logging

from Pyssembler.mips.hardware.exceptions import MIPSException, MIPSExceptionCodes, SyscallException

from ..hardware import GPR, CP0, MEM
from .sim_functions import get_sim_function_by_mnemonic
from .errors import *
from .syscall import simulate_syscall


import globals

if globals.GUI:
    __LOGGER__ = logging.getLogger('Pyssembler.SIM_THREAD')
else:
    __LOGGER__ = logging.getLogger('Pyssembler.SIMULATOR')


class Simulator():
    """
    Base Class for MIPS32 Simulators

    Provides all core components of a MIPS simulator. Also provides a function
    to assemble mips instructions
    """

    def __init__(self) -> None:

        # If step=True, wait for user input before executing next instr
        self.__step = False

        # Should be set if running in GUI mode
        self.__input_request_signal = None
        self.__input_line = None  # Set when input is recieved from GUI
        self.__output_request_signal = None

        # Observers
        self.__fetch_observers = []

    def start(self, pc_start=MEM.config.text_base_addr, step=False):
        """
        Starts MIPS32 simulator.

        Attributes
        ----------
        pc_start: int, default=memory.MemoryConfig.text_base_addr
            The first instruction address of the program
        step: bool, default=False
            If False, runs the entire simulation until the program stops. Setting to True
            allows to run each execution step with the execute_instruction function
        """
        self.__step = step

        __LOGGER__.debug('Initialzing environment...')
        # Set up the environment
        GPR.reset()
        CP0.reset()
        GPR.pc = pc_start
        GPR.write('$sp', MEM.config.stack_pointer)
        GPR.write('$gp', MEM.config.global_pointer)

        __LOGGER__.info(f'Starting simulator at PC={pc_start}...')
        if self.__step:
            __LOGGER__.debug('Step mode enabled, returning...')
            return
        __LOGGER__.debug('Step mode disabled, executing...')
        self.notify_fetch_observers(GPR.pc)
        while True:
            try:
                self.execute_instruction()
            except SimulationExitException:
                # Program stopped executing
                return

    def execute_instruction(self):
        """
        Executes the instruction located at PC

        Raises a SimulationExitException if the program stops. This
        could be caused by the following reasons:
        - Program dropped off
        - Exit system call was executed
        - Unhandled exception

        Returns the address of the instruction executed
        """
        instr = MEM.read_instruction(GPR.pc)
        if not instr:
            # No instruction at PC, program dropped off
            raise SimulationExitException('Program Dropped Off')
        sim_func = get_sim_function_by_mnemonic(instr.tokens[0].value)
        try:
            sim_func(instr)
        except MIPSException as e:
            # May Raise SimulationExitException, let it bubble up
            self.exception_handler(e)
        GPR.increment_pc()
        self.notify_fetch_observers(GPR.pc)
        return instr.memory_addr

    def exception_handler(self, exception: MIPSException):
        """
        The default exception handler. Performs necessary actions based on the
        exception code in exception.

        Raises SimulationExitException if there is no exception handler written to
        memory
        """
        if exception.exception_type == MIPSExceptionCodes.SYSCALL:
            # syscall executed
            simulate_syscall(exception.code, self)
            return
        if exception.exception_type == MIPSExceptionCodes.BKPT:
            # Halt simulation
            raise SimulationExitException('break instruction executed')
        if exception.exception_type == MIPSExceptionCodes.TRAP:
            # Halt simulation
            raise SimulationExitException('trap')
        if exception.exception_type == MIPSExceptionCodes.RI:
            raise SimulationExitException('attempted to execute a reserved instruction')

        # Set CP0 STATUS Register Exception Level bit
        CP0.write_status(exc_lvl=1)
        # Set CP0 CAUSE Register Exception Code
        CP0.write_cause(exc_code=exception.exception_type)
        # Write current PC to CP0 EPC
        CP0.write(CP0.EPC, GPR.pc)
        # If invalid memory address caused exception, set CP0 VADDR Register
        if exception.exception_type == MIPSExceptionCodes.ADDRL:
            CP0.write(CP0.VADDR, exception.address)
        if exception.exception_type == MIPSExceptionCodes.ADDRS:
            CP0.write(CP0.VADDR, exception.address)

        if not MEM.read_instruction(MEM.config.ktext_base_addr):
            # No exception handler was written to memory
            # LOGGER.info(str(exception))
            raise SimulationExitException(0)

    def link_input_request_signal(self, signal):
        self.__input_request_signal = signal

    def link_output_request_signal(self, signal):
        self.__output_request_signal = signal

    def send_input(self, input_str: str):
        self.__input_line = input_str

    def print(self, message):
        """
        Prints the message to either stdout or GUI based on how program is run
        """
        __LOGGER__.info('Print requested')
        message = str(message)
        if globals.GUI:
            # Send message to main thread via qt signal
            __LOGGER__.debug('Sending message to main thread...')
            self.__output_request_signal.emit(message)
            return
        # Print message using python's print() function
        __LOGGER__.debug('Printing message to STDOUT...')
        print(message, end='', flush=True)

    def input(self, prompt: str = None) -> str:
        """
        Get user input from either stdin or GUI based on how program is run.

        This function returns the user input as a string, it is up to the
        individual syscalls to parse and handle errors
        """
        __LOGGER__.info('Input requested...')
        if prompt:
            self.print(prompt)
        if globals.GUI:
            __LOGGER__.debug('Requesting input from GUI...')
            self.__input_request_signal.emit()
            # Wait until self.__input_line is set. This will happen when the
            # input_recieved signal is emitted and send_input() is called
            __LOGGER__.debug('Waiting for input...')
            while self.__input_line is None:
                pass
            __LOGGER__.debug('Input recieved')
            tmp, self.__input_line = self.__input_line, None
            return tmp
        # Get input via pythons input() function
        __LOGGER__.debug('Getting input from STDIN...')
        return input()

    def add_fetch_observer(self, observer):
        self.__fetch_observers.append(observer)

    def remove_fetch_observer(self, observer):
        self.__fetch_observers.remove(observer)

    def notify_fetch_observers(self, pc):
        for observer in self.__fetch_observers:
            observer(pc)
