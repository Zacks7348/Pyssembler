from ctypes import c_uint32, c_int32
from typing import Tuple

def __overflow_detection(a, b, s) -> bool:
    if a < 0 and b < 0 and s > 0:
        return True
    if a > 0 and b > 0 and s < 0:
        return True
    return False

def shift_left32(i: int, sa: int) -> int:
    """ Shift a 32-bit integer left 

    i << sa

    Returns
    -------
    int
        The resulting integer after shifting
    """
    return c_int32(i << sa).value

def shift_right32(i: int, sa: int, sign=False) -> int:
    """ Shift a 32-bit integer right 

    i >> sa

    Fill in bits by duplicating sign if sign=true,
    otherwise fill in with zeroes

    Returns
    -------
    int
        The resulting integer after shifting
    """
    if sign:
        bits = '{:032b}'.format(i)
        sign = bits[0]
        new_bits = (sign*sa) + bits
        return c_uint32(int(new_bits[:-sa], 2)).value
    return c_uint32(i >> sa)

def add32(a: int, b: int) -> Tuple[int, bool]:
    """ Add 2 32-bit integers

    a + b

    Returns
    -------
    tuple(int, bool)
        Returns the result and a bool (true if overflow occured)
    """
    s = c_int32(a + b).value
    return s, __overflow_detection(a, b, s)

def sub32(a: int, b: int) -> Tuple[int, bool]:
    """ sub 2 32-bit integers

    a - b

    Returns
    -------
    tuple(int, bool)
        Returns the result and a bool (true if overflow occured)
    """
    s = c_int32(a - b).value
    return s, __overflow_detection(a, b, s)

def and32(a: int, b: int) -> int:
    """ And 2 32-bit integers

    a & b
    Returns
    -------
    int
        Returns the 32 bit result
    """
    return c_int32(a & b).value

def div32(a: int, b: int) -> int:
    """Divide 2 32-bit integers

    a // b

    Returns
    -------
    int
        Returns quotient result
    """

    if b == 0:
        # According to the MIPS32 Instruction Set V6.06,
        # Division by zero produces an UNPREDICTABLE result
        # So instead of raising an error, just return 0
        # Might change to alert caller division by zero occured to 
        # produce warning or error
        return 0
    return c_int32(a // b).value

def mod32(a: int, b: int) -> int:
    """Modulo 2 32-bit integers

    a % b

    Returns
    -------
    int
        Returns remainder result
    """

    if b == 0:
        # According to the MIPS32 Instruction Set V6.06,
        # Division by zero produces an UNPREDICTABLE result
        # So instead of raising an error, just return 0
        # Might change to alert caller division by zero occured to 
        # produce warning or error
        return 0
    return c_int32(a % b).value

def mul32(a: int, b: int) -> int:
    """Muliply 2 32-bit integers

    a * b

    Returns
    -------
    int
        Returns LOW word
    """
    res = a * b
    return c_int32(res).value

def muh32(a: int, b: int) -> int:
    """Muliply 2 32-bit integers

    a * b

    Returns
    -------
    int
        Returns HIGH word
    """
    res = a * b
    return c_int32(res >> 32).value

def nor32(a: int, b: int) -> int:
    """NOR 2 32-bit integers

    ~(a | b)

    Returns
    -------
    int
        Returns HIGH word
    """

    return c_int32(~(a | b)).value

def or32(a: int, b: int) -> int:
    """OR 2 32-bit integers

    a | b

    Returns
    -------
    int
        Returns HIGH word
    """

    return c_int32(a | b).value

def xor32(a: int, b: int) -> int:
    """XOR 2 32-bit integers

    a | b

    Returns
    -------
    int
        Returns HIGH word
    """
    return c_int32((a & ~b) | (~a & b)).value