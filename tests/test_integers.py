# TODO: Write tests for mips/hardware/integer.py functions
from ctypes import (c_int64, c_int32, c_int16, c_int8,
                    c_uint64, c_uint32, c_uint16, c_uint8)
import unittest


# Module to test
from pyssembler.mips.hardware import integer


class TestIntegers(unittest.TestCase):
    def setUp(self) -> None:
        self.is_even_bits = [0 if x % 2 == 0 else 1 for x in range(64)]
        self.is_even_int = int(''.join([str(x) for x in reversed(self.is_even_bits)]), 2)

    def test_max_uint(self):
        with self.subTest('64-bit max uint'):
            self.assertEqual(c_uint64(-1).value, integer.max_uint(64))
        with self.subTest('32-bit max uint'):
            self.assertEqual(c_uint32(-1).value, integer.max_uint(32))
        with self.subTest('16-bit max uint'):
            self.assertEqual(c_uint16(-1).value, integer.max_uint(16))
        with self.subTest('8-bit max uint'):
            self.assertEqual(c_uint8(-1).value, integer.max_uint(8))

    def test_max_int(self):
        with self.subTest('64-bit max int'):
            self.assertEqual(0x7FFFFFFFFFFFFFFF, integer.max_int(64))
        with self.subTest('32-bit max int'):
            self.assertEqual(0x7FFFFFFF, integer.max_int(32))
        with self.subTest('16-bit max int'):
            self.assertEqual(0x7FFF, integer.max_int(16))
        with self.subTest('8-bit max int'):
            self.assertEqual(0x7F, integer.max_int(8))

    def test_min_int(self):
        with self.subTest('64-bit min int'):
            self.assertEqual(-0x8000000000000000, integer.min_int(64))
        with self.subTest('32-bit min int'):
            self.assertEqual(-0x80000000, integer.min_int(32))
        with self.subTest('16-bit min int'):
            self.assertEqual(-0x8000, integer.min_int(16))
        with self.subTest('8-bit min int'):
            self.assertEqual(-0x80, integer.min_int(8))

    def test_get_bit(self):
        for i in range(64):
            with self.subTest(f'Get bit {i}'):
                self.assertEqual(self.is_even_bits[i], integer.get_bit(self.is_even_int, i))

    def test_set_bit(self):
        for i in range(64):
            with self.subTest(f'Set bit {i}'):
                self.assertEqual(2 ** i, integer.set_bit(0, i))

    def test_clear_bit(self):
        for i in range(64):
            with self.subTest(f'Invert bit {i}'):
                self.assertEqual(
                    0,
                    integer.get_bit(integer.clear_bit(self.is_even_int, i), i)
                )

    def test_invert_bit(self):
        for i in range(64):
            with self.subTest(f'Invert bit {i}'):
                self.assertNotEqual(
                    self.is_even_bits[i],
                    integer.get_bit(integer.invert_bit(self.is_even_int, i), i)
                )

    def test_to_uint(self):
        step = (integer.MAX_UINT64 - integer.MIN_INT64) // 20
        for i in range(integer.MIN_INT64, integer.MAX_UINT64+1, step):
            with self.subTest(f'64-bit to uint: {i}'):
                self.assertEqual(c_uint64(i).value, integer.to_uint(i, 64))
            with self.subTest(f'32-bit to uint: {i}'):
                self.assertEqual(c_uint32(i).value, integer.to_uint(i, 32))
            with self.subTest(f'16-bit to uint: {i}'):
                self.assertEqual(c_uint16(i).value, integer.to_uint(i, 16))
            with self.subTest(f'8-bit to uint: {i}'):
                self.assertEqual(c_uint8(i).value, integer.to_uint(i, 8))

    def test_to_int(self):
        step = (integer.MAX_UINT64 - integer.MIN_INT64) // 20
        for i in range(integer.MIN_INT64, integer.MAX_UINT64 + 1, step):
            with self.subTest(f'64-bit to int: {i}'):
                self.assertEqual(c_int64(i).value, integer.to_int(i, 64))
            with self.subTest(f'32-bit to int: {i}'):
                self.assertEqual(c_int32(i).value, integer.to_int(i, 32))
            with self.subTest(f'16-bit to int: {i}'):
                self.assertEqual(c_int16(i).value, integer.to_int(i, 16))
            with self.subTest(f'8-bit to int: {i}'):
                self.assertEqual(c_int8(i).value, integer.to_int(i, 8))
