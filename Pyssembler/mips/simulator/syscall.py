import logging

from Pyssembler.mips.hardware.types import MemorySize
from ..hardware import registers, memory
from .errors import SimulationExitException

LOGGER = logging.getLogger('PYSSEMBLER.SYSCALL')

class SyscallCodes:
    PRINT_INT = 1
    PRINT_FLOAT = 2
    PRINT_DOUBLE = 3
    PRINT_STRING = 4
    READ_INT = 5
    READ_FLOAT = 6
    READ_DOUBLE = 7
    READ_STRING = 8
    SBRK = 9 # Allocated Heap Memory
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
    return registers.gpr_read('$a0'), registers.gpr_read('$a1'), registers.gpr_read('$a2')

def __print_int():
    LOGGER.debug('Printing integer...')
    int_val, _, _ = __get_args()
    print(int_val, end='')

def __print_str():
    LOGGER.debug('Printing string...')
    read_addr, _, _ = __get_args()
    i = 0
    while (c := chr(memory.read_byte(read_addr+i))) != '\0':
        # If string is not null-terminated, infinite loop inbound
        # need to implement check for this
        print(c, end='', flush=True)
        i += 1

def __read_int():
    LOGGER.debug('Reading integer...')
    try:
        read_int = int(input())
    except ValueError:
        raise ValueError('Expected to read an int')
    registers.gpr_write('$v0', read_int)
    LOGGER.debug('Successfully read integer: {} into $v0'.format(read_int))

def __read_str():
    LOGGER.debug('Reading string...')
    buffer, max_length, _ = __get_args()
    read_str = input()
    for i, c in enumerate(read_str):
        if i >= max_length-1:
            # Exceeded char limit
            return
        memory.write(buffer+i, ord(c), MemorySize.BYTE)
    LOGGER.debug('Successfully read string: {} into MEM[{}]'.format(read_str, buffer))

def __sbrk():
    LOGGER.debug('Allocating bytes in heap...')
    num_bytes, _, _ = __get_args()
    addr = memory.allocate_heap_bytes(num_bytes)
    registers.gpr_write('$v0', addr)
    LOGGER.debug('Done!')

def __exit():
    LOGGER.debug('Exiting...')
    raise SimulationExitException()

def __print_char():
    LOGGER.debug('Printing char...')
    read_addr, _, _ = __get_args()
    print(chr(registers.gpr_read(read_addr)), end='')

def __read_char():
    LOGGER.debug('Reading char...')
    read_char = input()
    registers.gpr_write('$v0', ord(read_char))
    LOGGER.debug('Successfully read char: {} into $v0'.format(read_char))

def __exit_with_value():
    LOGGER.debug('Exiting with value...')
    result, _, _ = __get_args()
    raise SimulationExitException(result)

def simulate_syscall(code):
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

    LOGGER.debug('Simulating SYSCALL...')
    sim = mappings[code]
    if not sim: 
        LOGGER.error('Invalid SYSCALL code')
        raise ValueError('Invalid SYSCALL code: {}'.format(code))
    sim()
    LOGGER.debug('Finished!')
