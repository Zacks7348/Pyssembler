from ctypes import c_int32, c_uint32 
from typing import Union

MAX_UINT32 = 0xffffffff
MAX_SINT32 = 0x7fffffff
MIN_SINT32 = -0x80000000

DWORD = 64
WORD = 32
HWORD = 16
BYTE = 8
BIT = 1

WORD_LENGTH_BYTES = WORD // BYTE
HWORD_LENGTH_BYTES = HWORD // BYTE

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

if __name__ == '__main__':
    val = -8
    string = Integer.to_bin_string(val)
    print(string)
    print(Integer.from_bin_string(string, signed=True))