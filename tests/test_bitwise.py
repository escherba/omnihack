__author__ = 'escherba'

import unittest
import random
import sys
import struct
from functools import partial
from pymaptools.bitwise import packl_ctypes, hamming, hamming_from_iter, bitlist


class TestBitwise(unittest.TestCase):
    def test_packing(self):
        """Pack 100 random long integers"""

        def unpack1(seq):
            return struct.unpack(frmt, seq)[0]

        def random_int():
            return random.randint(0, sys.maxint)

        frmt, size = '>Q', 8 * 8
        pack1 = partial(struct.pack, frmt)
        pack2 = partial(packl_ctypes, size)

        for _ in range(100):
            rlong = long(random_int())
            packed1 = pack1(rlong)
            packed2 = pack2(rlong)
            self.assertEqual(packed1, packed2)
            self.assertEqual(rlong, unpack1(packed1))

    def test_packing2(self):
        pack2 = partial(packl_ctypes, 16 * 8)
        packed128 = pack2(long((1 << 128) - 1))
        self.assertEqual(packed128, '\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff')
        packed128b = pack2(long((1 << 128) - 2))
        self.assertEqual(packed128b, '\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xfe')
        packed128c = pack2(long(1 << 127))
        self.assertEqual(packed128c, '\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
        packed64 = pack2(long((1 << 64) - 1))
        self.assertEqual(packed64, '\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\xff\xff\xff\xff\xff\xff')
        packed64b = pack2(long((1 << 64) - 2))
        self.assertEqual(packed64b, '\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\xff\xff\xff\xff\xff\xfe')

    def test_hamming(self):
        """Correctly calculate Hamming distances between numbers"""
        for _ in range(100):
            num1 = random.randint(0, sys.maxint)
            num2 = random.randint(0, sys.maxint)
            self.assertEqual(hamming(num1, num2),
                             hamming_from_iter(bitlist(num1), bitlist(num2)))


if __name__ == '__main__':
    unittest.main()
