#!/usr/bin/env python3
import unittest
from array import array

import common

from tomb.aes.constants import *
from tomb.aes.gf2 import *


def derive_galois_multiplication_table(n):
    tab = array("B", b"\0" * 256)
    for i in range(256):
        tab[i] = gf2_8_mul(i, n)
    return tab


class TestAESConstants(unittest.TestCase):

    # "Test" the constants by deriving them.

    def test_verify_gmul2_lut(self):
        self.assertEqual(GMUL2_LUT, derive_galois_multiplication_table(2))

    def test_verify_gmul3_lut(self):
        self.assertEqual(GMUL3_LUT, derive_galois_multiplication_table(3))

    def test_verify_gmul9_lut(self):
        self.assertEqual(GMUL09_LUT, derive_galois_multiplication_table(9))

    def test_verify_gmul11_lut(self):
        self.assertEqual(GMUL11_LUT, derive_galois_multiplication_table(11))

    def test_verify_gmul13_lut(self):
        self.assertEqual(GMUL13_LUT, derive_galois_multiplication_table(13))

    def test_verify_gmul14_lut(self):
        self.assertEqual(GMUL14_LUT, derive_galois_multiplication_table(14))


if __name__ == "__main__":
    unittest.main()
