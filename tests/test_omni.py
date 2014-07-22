#!/usr/bin/env python2

import unittest
from pymaptools import enumerator


class TestEnum(unittest.TestCase):
    def test_values(self):
        i = enumerator()
        self.assertEqual(i["cat"], 0)
        self.assertEqual(i["dog"], 1)
        self.assertEqual(i["cat"], 0)
        self.assertEqual(len(i), 2)


if __name__ == "__main__":
    unittest.run(verbose=True)
