#!/usr/bin/python
from __future__ import print_function
from omnihack import enumerator
import unittest
import sys

try:
    import test.support as test_support  # Python 3
except ImportError:
    import test.test_support as test_support  # Python 2


class TestOmni(unittest.TestCase):
    def test_values(self):
        i = enumerator()
        self.assertEqual(i["cat"], 0)
        self.assertEqual(i["dog"], 1)
        self.assertEqual(i["cat"], 0)
        self.assertEqual(len(i), 2)


def test_main(verbose=None):

    test_classes = [TestOmni]
    test_support.run_unittest(*test_classes)

    # verify reference counting
    if verbose and hasattr(sys, "gettotalrefcount"):
        import gc
        counts = [None] * 5
        for i in xrange(len(counts)):
            test_support.run_unittest(*test_classes)
            gc.collect()
            counts[i] = sys.gettotalrefcount()
        print(counts)

if __name__ == "__main__":
    test_main(verbose=True)
