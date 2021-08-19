from ctypes import c_int32, c_uint32
from pdb import set_trace
from typing import Union

from .types import MemorySize

__ESCAPE_CHARS__ = {'"': '\"', '\\': '\\', 'n': '\n',
                    'r': '\r', 't': '\t', 'b': '\b',
                    '0': '\0'}


class Integer:
    """
    Utility class that provides functions for manipulating
    bits of a 32-bit int
    """

    @staticmethod
    def from_bin_string(b: str, signed=False) -> int:
        """
        Converts both signed and unsigned binary strings into
        ints
        """
        if signed:
            return c_int32(int(b, 2)).value
        return c_uint32(int(b, 2)).value

    @staticmethod
    def from_string(value: str) -> int:
        """
        Try to convert the value in a string to an int

        Supported strings are (1, 0b1, 0o1, 0x1, 1E+1)

        Parameters
        ----------
        value : str
            The string to be converted

        Returns
        -------
        int
            The integer found or None
        """
        #import pdb; pdb.set_trace()
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
        elif value.startswith('0b'):
            # value is a binary number
            try: res = int(value, 2)
            except: return None
        elif value.startswith('0o'):
            # value is an octal number
            try: res = int(value, 8)
            except: return None
        elif value.startswith('0x'):
            # value is a hex number
            try: res = int(value, 16)
            except: return None
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
                res = int(leading) * (10**int(exp))
            except:
                return None
        else: return None
        if negative: return res * -1
        return res

    @staticmethod
    def to_bin_string(i: int, bits=32):
        """
        Converts ints into signed and unsigned binary strings
        """
        return '{:032b}'.format(c_uint32(i).value)[32-bits:]

    @staticmethod
    def get_bits(i: int, low: int, high: int, signed=False) -> int:
        """
        Returns a specified range of bits from i. Assumes bit 31 is left most bit
        """
        mask = 0
        for power in range(low, high+1):
            mask += 2**power
        bits = (i & mask) >> low

        if not signed:
            return bits

        # perform sign extension to 32 bits
        sign = bits
        for _ in range(low, high):
            sign >>= 1
        if sign == 0:
            return bits
        mask = 0
        for power in range(high+1, 32):
            mask += 2**power
        return c_int32(bits | mask).value

    @staticmethod
    def get_bit(i: int, bit: int) -> int:
        return Integer.get_bits(i, bit, bit)
    
    @staticmethod
    def get_byte(i:int, byte_num: int) -> int:
        """
        Return a specific byte from an integer

        Byte 0 represents the first 
        """
        scale = byte_num*MemorySize.BYTE
        return Integer.get_bits(i, scale, scale+MemorySize.BYTE-1)

    @staticmethod
    def signed_to_unsigned(i: int) -> int:
        """
        Returns unsigned int from a signed int
        """
        return c_uint32(i).value

    @staticmethod
    def unsigned_to_signed(i: int) -> int:
        """
        Returns signed int from an unsigned int
        """
        return c_int32(i).value


def parse_ascii(ascii_val: str) -> str:
    """
    Parses a string read from a file and returns the true string
    """

    if not ascii_val.startswith('"') or not ascii_val.endswith('"'):
        # ascii value must be wrapped in double quotes
        return None
    
    if ascii_val == '"': return None
    if ascii_val == '""': return ''

    escaped = ''
    escaping = False

    for i, c in enumerate(ascii_val[1:-1]):
        if not escaping:
            if c == '\\':
                escaping = True
                continue
            if c == '"' and i < len(ascii_val) - 2:
                # String ended early
                return None
            else:
                escaped += c
        else:
            if c in __ESCAPE_CHARS__:
                escaped += __ESCAPE_CHARS__[c]
            else:
                escaped += '\\' + c
            escaping = False
    if escaping:
        escaped += '\\'
    return escaped

# Some util functions for decoding a binary instruction

def get_op(instr: int) -> int:
    return Integer.get_bits(instr, 26, 31)

def get_reg1(instr: int) -> int:
	return Integer.get_bits(instr, 21, 25)

def get_reg2(instr: int) -> int:
	return Integer.get_bits(instr, 16, 20)

def get_reg3(instr: int) -> int:
	return Integer.get_bits(instr, 11, 15)

def get_shamt(instr: int) -> int:
	return Integer.get_bits(instr, 6, 10)

def get_func(instr: int) -> int:
    return Integer.get_bits(instr, 0, 5)


if __name__ == '__main__':
    val = -8
    string = Integer.to_bin_string(val)
    print(string)
    print(Integer.from_bin_string(string, signed=True))
