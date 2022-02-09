import logging

from Pyssembler.mips.hardware.types import MemorySize
from ..hardware import GPR, MEM
from .errors import ExitSimulation

import globals
if globals.GUI:
    __LOGGER__ = logging.getLogger('Pyssembler.SIM_THREAD')
else:
    __LOGGER__ = logging.getLogger('Pyssembler.SYSCALL')


class SyscallCodes:
    PRINT_INT = 1
    PRINT_FLOAT = 2
    PRINT_DOUBLE = 3
    PRINT_STRING = 4
    READ_INT = 5
    READ_FLOAT = 6
    READ_DOUBLE = 7
    READ_STRING = 8
    SBRK = 9  # Allocate Heap Memory
    EXIT = 10
    PRINT_CHAR = 11
    READ_CHAR = 12
    OPEN_FILE = 13
    READ_FROM_FILE = 14
    WRITE_TO_FILE = 15
    CLOSE_FILE = 16
    EXIT_WITH_VALUE = 17


def get_syscalls():
    """
    Return the list of implemented syscalls, their codes, 
    and their descriptions
    """
    return {
        SyscallCodes.PRINT_INT: {
            'service': 'PRINT INTEGER',
            'args': '$a0 = integer to print',
            'result': ''},
        SyscallCodes.PRINT_STRING: {
            'service': 'PRINT STRING',
            'args': '$a0 = address of null-terminated string',
            'result': ''},
        SyscallCodes.READ_INT: {
            'service': 'READ INTEGER',
            'args': '',
            'result': '$v0 contains the integer read'},
        SyscallCodes.READ_STRING: {
            'service': 'READ STRING',
            'args': '$a0 = address of input buffer, $a1 = max chars',
            'result': ''
        }
    }


def __get_args():
    return GPR.read('$a0'), GPR.read('$a1'), GPR.read('$a2')


def __print_int(sim):
    int_val, _, _ = __get_args()
    __LOGGER__.debug(f'Printing integer: {int_val}...')
    __LOGGER__.debug(int_val)
    sim.print(int_val)


def __print_str(sim):
    __LOGGER__.debug('Printing string...')
    read_addr, _, _ = __get_args()
    i = 0
    while (c := chr(MEM.read_byte(read_addr + i))) != '\0':
        # If string is not null-terminated, infinite loop inbound
        # need to implement check for this
        sim.print(c)
        i += 1


def __read_int(sim):
    __LOGGER__.debug('Reading integer...')
    try:
        read_int = int(sim.input())
    except ValueError:
        raise ValueError('Expected to read an int')
    GPR.write('$v0', read_int)


def __read_str(sim):
    __LOGGER__.debug('Reading string...')
    buffer, max_length, _ = __get_args()
    read_str = sim.input()
    for i, c in enumerate(read_str):
        if i >= max_length - 1:
            # Exceeded char limit
            return
        MEM.write(buffer + i, ord(c), MemorySize.BYTE)


def __sbrk(sim):
    __LOGGER__.debug('Allocating bytes in heap...')
    num_bytes, _, _ = __get_args()
    addr = MEM.allocate_heap_bytes(num_bytes)
    GPR.write('$v0', addr)
    # LOGGER.debug('Done!')


def __exit(sim):
    __LOGGER__.debug('Exiting...')
    raise ExitSimulation()


def __print_char(sim):
    __LOGGER__.debug('Printing char...')
    read_addr, _, _ = __get_args()
    sim.print(chr(GPR.read(read_addr)))


def __read_char(sim):
    __LOGGER__.debug('Reading char...')
    read_char = sim.input()
    GPR.write('$v0', ord(read_char))


def __exit_with_value():
    __LOGGER__.debug('Exiting with value...')
    result, _, _ = __get_args()
    raise ExitSimulation(result)


def simulate_syscall(code, sim):
    mappings = {
        SyscallCodes.PRINT_INT: __print_int,
        SyscallCodes.PRINT_STRING: __print_str,
        SyscallCodes.READ_INT: __read_int,
        SyscallCodes.READ_STRING: __read_str,
        SyscallCodes.SBRK: __sbrk,
        SyscallCodes.EXIT: __exit,
        SyscallCodes.PRINT_CHAR: __print_char,
        SyscallCodes.READ_CHAR: __read_char,
        SyscallCodes.EXIT_WITH_VALUE: __exit_with_value
    }

    __LOGGER__.debug('Simulating SYSCALL...')
    syscall_sim = mappings[code]
    if not sim:
        # LOGGER.error('Invalid SYSCALL code')
        raise ValueError('Invalid SYSCALL code: {}'.format(code))
    syscall_sim(sim)
