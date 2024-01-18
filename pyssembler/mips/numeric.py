"""
This file contains logic for handling signed/unsigned integers of a fixed
number of bits.

Python 3 does not implement fixed-size integer types. Instead, all integers
are considered signed integers of unlimited size. This file provides a way of
working with "fixed-size" signed and unsigned integers using Python integers.

Values are coerced into "fixed-sizes" by masking the true value to the correct
bit length.

Byte-endianness of integers is determined by the system this program is running on.
"""
import struct
import typing

from . import constants

PREFIXES = {
    '0b': 2,
    '0o': 8,
    '0x': 16
}

# ------------------------------------------------------------------------
# Useful constants
# ------------------------------------------------------------------------
MAX_UINT64 = 0xFFFFFFFFFFFFFFFF  # 18,446,744,073,709,551,615
MAX_INT64 = 0x7FFFFFFFFFFFFFFF  # 9,223,372,036,854,775,807
MIN_INT64 = -0x8000000000000000  # -9,223,372,036,854,775,808

MAX_UINT32 = 0xFFFFFFFF  # 4,294,967,295
MAX_INT32 = 0x7FFFFFFF  # 2,147,483,647
MIN_INT32 = -0x80000000  # -2,147,483,648

MAX_UINT16 = 0xFFFF  # 65,535
MAX_INT16 = 0x7FFF  # 32,767
MIN_INT16 = -0x8000  # -32,768

MAX_UINT8 = 0xFF  # 255
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
    for i in range(low, high):
        bit = new_bits & 1
        value = set_bit(value, i) if bit else clear_bit(value, i)
        new_bits >>= 1
    return value


def get_bit(value: int, bit: int) -> int:
    """
    Read a specific bit from a value

    :param value: The value to read
    :param bit: The bit to return
    :return: int
    """
    return (value >> bit) & 1


def get_bits(value: int, low: int, high: int) -> int:
    """
    Returns the bits located in value[low:high+1]

    :param value: The value to get bits from
    :param low: The low bit index
    :param high: The high bit index
    :return: int
    """
    res = 0
    for i, bit in enumerate(range(low, high)):
        res |= (get_bit(value, bit) << i)
    return res


def get_byte(value: int, byte_num: int) -> int:
    """
    Read a specific byte from a value

    :param value: The value to read
    :param byte_num: The byte to read
    :return: int
    """
    scale = byte_num * 8
    return get_bits(value, scale, scale + 8)


def get_bytes(value: int, low: int, high: int) -> int:
    res = 0
    for i, byte in enumerate(range(low, high)):
        res |= (get_byte(value, byte) << i * constants.BYTE)

    return res


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


def to_bytes(value: int, num_bytes: int) -> typing.List[int]:
    """
    Convert an integer to a list of bytes.

    Byte-Endianness is determined by the system
    """
    return [get_byte(value, byte) for byte in reversed(range(num_bytes))]


def from_bytes(int_bytes: typing.List[int], size: int = 32, signed=False) -> int:
    """
    Build an integer from a list of bytes. The size of the integer is
    determined by the number of bytes passed in.

    if signed is True, then a signed integer is returned

    :param int_bytes: The list of bytes representing an integer
    :param signed: If True returns a signed integer
    :return: the represented int
    """
    res = 0
    for i, byte in enumerate(reversed(int_bytes)):
        res |= byte << (i * constants.BYTE)

    return to_int(res, size) if signed else to_uint(res, size)


def to_double(i: int) -> float:
    return struct.unpack('d', struct.pack('q', i))[0]


def to_float(i: int) -> float:
    return struct.unpack('f', struct.pack('i', i))[0]


def from_double(f: float, size: int = constants.WORD, signed: bool = False) -> int:
    res = struct.unpack('q', struct.pack('d', f))[0]
    return to_int(res, size=size) if signed else to_uint(res, size=size)


def from_float(f: float,  size: int = constants.WORD, signed: bool = False) -> int:
    res = struct.unpack('i', struct.pack('f', f))[0]
    return to_int(res, size=size) if signed else to_uint(res, size=size)


# ------------------------------------------------------------------------
# String shenanigans
# ------------------------------------------------------------------------
def to_string(value: int, radix=int, size: int = 32, prefix: bool = False) -> str:
    """
    Represent the value as a string

    :param value: The value to convert
    :param radix: How to represent the value (bin, oct, int, hex)
    :param size:
    :param prefix:
    :return:
    """
    if radix == int:
        return f'{value}'
    if radix == bin:
        return f'{"0b" if prefix else ""}{value:0{size}b}'
    if radix == hex:
        return f'{"0x" if prefix else ""}{value:0{size//4}x}'
    raise ValueError(f'Invalid radix: {radix}')


def from_string(value: str, signed: bool = True, size: int = 32) -> typing.Union[int, float]:
    """
    Try to convert the value in a string to an int.
    Supported strings are (1, 0b1, 0o1, 0x1, 1E+1, 'b').

    :param value: The string to convert
    :param signed: If True, return as a signed int (default=True)
    :param size: The number of bits to represent the integer
    :return: int
    """
    try:
        # This will work if value is an integer in any of these formats:
        # 1, 0b1, 0o1, 0x1
        return int(value, PREFIXES.get(value[:2], 10))
    except:
        pass

    try:
        # This will work if value is in any of these formats:
        # 1.0, 1E+1, 1.2e-1
        res = float(value)
        return res if not float.is_integer(res) else int(res)
    except:
        pass

    # Char literals
    # Use eval() to get a single character from value. eval() should never
    # be ran on untrusted input. To achieve trust we first check that value
    # is surrounded by single quotes and has a length of 3 or 4. This ensures
    # that value will be evaluated as a Python string.
    if len(value) in {3, 4} and value[0] == value[-1] == "'":
        try:
            return ord(eval(value))
        except:
            pass

    return None

