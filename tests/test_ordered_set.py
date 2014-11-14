from pymaptools.queue import OrderedSet
import pickle
import unittest


class TestOrderedSet(unittest.TestCase):
    def test_pickle(self):
        set1 = OrderedSet('abracadabra')
        roundtrip = pickle.loads(pickle.dumps(set1))
        self.assertEqual(roundtrip, set1)

    def test_empty_pickle(self):
        empty_oset = OrderedSet()
        empty_roundtrip = pickle.loads(pickle.dumps(empty_oset))
        self.assertEqual(empty_roundtrip, empty_oset)

    def test_order(self):
        set1 = OrderedSet('abracadabra')
        self.assertEqual(len(set1), 5)
        self.assertEqual(set1, OrderedSet(['a', 'b', 'r', 'c', 'd']))
        self.assertEqual(list(reversed(set1)), ['d', 'c', 'r', 'b', 'a'])

    def test_binary_operations(self):
        set1 = OrderedSet('abracadabra')
        set2 = OrderedSet('simsalabim')
        self.assertNotEqual(set1, set2)

        self.assertEqual(set1 & set2, OrderedSet(['a', 'b']))
        self.assertEqual(set1 | set2, OrderedSet(['a', 'b', 'r', 'c', 'd', 's', 'i', 'm', 'l']))
        self.assertEqual(set1 - set2, OrderedSet(['r', 'c', 'd']))

    def test_slicing(self):
        set1 = OrderedSet('abracadabra')
        self.assertEqual(set1[:], set1)
        self.assertEqual(set1.copy(), set1)
        self.assertIs(set1[:], set1)
        self.assertIsNot(set1.copy(), set1)

        self.assertEqual(set1[[1, 2]], OrderedSet(['b', 'r']))
        self.assertEqual(set1[1:3], OrderedSet(['b', 'r']))

    def test_maxlen(self):
        setm = OrderedSet(maxlen=3)
        setm.add("a")
        setm.add("b")
        setm.add("c")
        setm.add("d")
        self.assertEqual(setm, OrderedSet(['b', 'c', 'd']))
