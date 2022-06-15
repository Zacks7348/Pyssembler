"""
This file contains logic for handling signed/unsigned integers of a fixed
number of bits. Python by design does not implement fixed-size data types
due to its dynamic nature.

For usual sizes (2, 4, 8, 16, 32, ... bits) one could use the ctypes library,
which provides c-type integers. However, there are cases where we would like
to work with integers with 5 bits and other unusal sizes.
"""

from pyssembler.mips.hardware import MemorySize

# ------------------------------------------------------------------------
# Useful constants
# ------------------------------------------------------------------------

# Integers
MAX_UINT64 = 0xFFFFFFFFFFFFFFFF  # 18,446,744,073,709,551,615
MAX_INT64 = 0x7FFFFFFFFFFFFFFF  # 9,223,372,036,854,775,807
MIN_INT64 = -0x8000000000000000  # -9,223,372,036,854,775,808

MAX_UINT32 = 0xFFFFFFFF  # 4,294,967,295
MAX_INT32 = 0x7FFFFFFF  # 2,147,483,647
MIN_INT32 = -0x80000000  # -2,147,483,648

MAX_UINT16 = 0xFFFF  # 65,535
MAX_INT16 = 0x7FFF  # 32,767
MIN_INT16 = -0x8000  # -32,768

MAX_UINT8 = 0xFF  # 258
MAX_INT8 = 0x7F  # 127
MIN_INT8 = -0x80  # -128


# ------------------------------------------------------------------------
# Calculating max/min of variable-sized integers
# ------------------------------------------------------------------------
def max_uint(size: int) -> int:
    """
    Returns the largest unsigned integer that can be stored with size bits
    :param size: The number of bits
    :return: max int
    """
    return 2 ** size - 1


def max_int(size: int) -> int:
    """
    Returns the largest signed integer that can be stored with size bits
    :param size: The number of bits
    :return: max int
    """
    return ((2 ** size) // 2) - 1


def min_int(size: int) -> int:
    """
    Returns the smallest signed integer that can be stored with size bits
    :param size: The number of bits
    :return: max int
    """
    return (2 ** size / 2) * -1


# ------------------------------------------------------------------------
# Bit manipulation
# ------------------------------------------------------------------------
def set_bit(value: int, bit: int) -> int:
    """
    Set the ith bit in value
    :param value: The value to manipulate
    :param bit: The bit to set
    :return: The new integer
    """
    return value | (1 << bit)


def clear_bit(value: int, bit: int) -> int:
    """
    Clear the ith bit in value
    :param value: The value to manipulate
    :param bit: The bit to clear
    :return: The new integer
    """
    return value & ~(1 << bit)


def invert_bit(value: int, bit: int) -> int:
    """
    Invert the ith bit in a value
    :param value: The value to manipulate
    :param bit: The bit to invert
    :return: The new integer
    """
    return value ^ (1 << bit)


def change_bits(value: int, low: int, high: int, new_bits: int) -> int:
    """
    Change the bits in value[low:high+1] to the first n bits in new_bits
    :param value: The value to write new bits into
    :param low: Where to start writing new bits
    :param high: Where to stop writing new bits
    :param new_bits: The new bits to write
    :return: The new integer
    """
    mask = 1
    for bit in range(low, high+1):
        if new_bits & mask:
            value = set_bit(value, bit)
        else:
            value = clear_bit(value, bit)
        new_bits >>= 1
    return value


def get_bits(value: int, low: int, high: int) -> int:
    """
    Returns the bits located in value[low:high+1]
    :param value: The value to get bits from
    :param low: The low bit index
    :param high: The high bit index
    :return: int
    """
    mask = 0
    for power in range(low, high+1):
        mask += 2**power
    return (value & mask) >> low


def get_bit(value: int, bit: int) -> int:
    """
    Read a specific bit from a value
    :param value: The value to read
    :param bit: The bit to return
    :return: int
    """
    return get_bits(value, bit, bit)


def get_byte(value: int, byte_num: int) -> int:
    """
    Read a specific byte from a value
    :param value: The value to read
    :param byte_num: The byte to read
    :return: int
    """
    scale = byte_num * MemorySize.BYTE
    return get_bits(value, scale, scale+MemorySize.BYTE-1)


# ------------------------------------------------------------------------
# Converting python integers
# ------------------------------------------------------------------------
def to_uint(value: int, size: int = 32) -> int:
    """
    Return the value as an unsigned integer with size bits
    :param value: The value to convert
    :param size: The number of bits to represent the unsigned integer
    :return: unsigned int
    """
    # Handle easy case first
    if 0 <= value <= max_uint(size):
        return value

    # Build a mask with size bits
    mask = 1
    for i in range(1, size):
        mask |= (1 << i)
    return value & mask


def to_int(value: int, size: int = 32) -> int:
    """
    Return the value as a signed integer with size bits
    :param value: The value to convert
    :param size: The number of bits to represent the integer
    :return: signed int
    """
    # Handle easy case first
    if min_int(size) <= value <= max_int(size):
        return value

    mask = (2 ** size) - 1
    if value & (1 << (size - 1)):
        return value | ~mask
    else:
        return value & mask


# ------------------------------------------------------------------------
# String shenanigans
# ------------------------------------------------------------------------
def to_string(value: int, radix = int, size: int = 32, prefix: bool = False) -> str:
    """
    Represent the value as a string
    :param value: The value to convert
    :param radix: How to represent the value (bin, oct, int, hex)
    :param size:
    :param prefix:
    :return:
    """
    if radix == int:
        return f'{value:0{size}d}'
    if radix == bin:
        return f'{"0b" if prefix else ""}{value:0{size}b}'
    if radix == oct:
        return f'{"0o" if prefix else ""}{value:0{size}o}'
    if radix == hex:
        return f'{"0x" if prefix else ""}{value:0{size}x}'
    raise ValueError(f'Invalid radix: {radix}')


def from_string(value: str, signed: bool = True, size: int = 32) -> int:
    """
    Try to convert the value in a string to an int
    Supported strings are (1, 0b1, 0o1, 0x1, 1E+1)
    :param value: The string to convert
    :param signed: If True, return as a signed int (default=True)
    :param size: The number of bits to represent the integer
    :return: int
    """
    if '.' in value:
        # An integer cannot have a period
        return None
    negative = False
    res = None
    if value.startswith('-'):
        # if value is an integer, it is negative
        negative = True
        value = value.replace('-', '', 1)
    if value.startswith("'") and value.endswith("'"):
        # value should be a char
        # value should be 'c' 3 chars
        if len(value) == 3:
            res = ord(value[1:2])
        else:
            return None
    elif value.startswith('0b'):
        # value is a binary number
        try:
            res = int(value, 2)
        except:
            return None
    elif value.startswith('0o'):
        # value is an octal number
        try:
            res = int(value, 8)
        except:
            return None
    elif value.startswith('0x'):
        # value is a hex number
        try:
            res = int(value, 16)
        except:
            return None
    elif value.isnumeric():
        res = int(value)
    elif 'e' in value or 'E' in value:
        value = value.lower()
        leading = ''
        exp = ''
        before_e = True
        for c in value:
            if before_e:
                if c == 'e':
                    before_e = False
                    continue
                if c.isnumeric() or c == '-':
                    leading += c
                else:
                    return None
            else:
                if c.isnumeric() or c == '-':
                    exp += c
                elif c == '+':
                    pass
                else:
                    return None
        try:
            res = int(leading) * (10 ** int(exp))
        except:
            return None
    else:
        return None
    if negative:
        res *= -1
    if signed:
        return to_int(res, size)
    return to_uint(res, size)


if __name__ == '__main__':
    from ctypes import c_uint8
    print(to_int(128, 8))
