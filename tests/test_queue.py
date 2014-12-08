from pymaptools.queue import OrderedSet, Heap
import time
import pickle
import unittest


class TestOrderedSet(unittest.TestCase):
    def test_serialize(self):
        set1 = OrderedSet('abracadabra')
        roundtrip = pickle.loads(pickle.dumps(set1))
        self.assertEqual(roundtrip, set1)
        empty_oset = OrderedSet()
        self.assertEqual(repr(empty_oset), "OrderedSet()")
        empty_roundtrip = pickle.loads(pickle.dumps(empty_oset))
        self.assertEqual(empty_roundtrip, empty_oset)
        set2 = OrderedSet("abc")
        self.assertEqual(repr(set2), "OrderedSet(['a', 'b', 'c'])")

    def test_order(self):
        set1 = OrderedSet('abracadabra')
        self.assertEqual(len(set1), 5)
        self.assertEqual(set1, OrderedSet(['a', 'b', 'r', 'c', 'd']))
        self.assertEqual(list(reversed(set1)), ['d', 'c', 'r', 'b', 'a'])

    def test_binary_operations(self):
        text1 = 'abracadabra'
        set1 = OrderedSet(text1)
        set2 = OrderedSet('simsalabim')
        self.assertNotEqual(set1, set2)
        self.assertNotEqual(set1, 9)
        self.assertEqual(set1, set(text1))

        self.assertEqual(set1 & set2, OrderedSet(['a', 'b']))
        self.assertEqual(set1 | set2, OrderedSet(['a', 'b', 'r', 'c', 'd', 's', 'i', 'm', 'l']))
        self.assertEqual(set1 - set2, OrderedSet(['r', 'c', 'd']))

    def test_slicing(self):
        set1 = OrderedSet('abracadabra')
        self.assertEqual(set1[0], "a")
        self.assertEqual(set1[:], set1)
        self.assertEqual(set1.copy(), set1)
        self.assertIs(set1[:], set1)
        self.assertIsNot(set1.copy(), set1)

        self.assertEqual(set1[[1, 2]], OrderedSet(['b', 'r']))
        self.assertEqual(set1[1:3], OrderedSet(['b', 'r']))

        with self.assertRaises(TypeError):
            set1.__getitem__("abc")

    def test_maxlen(self):
        setm = OrderedSet(maxlen=3)
        setm.add("a")
        setm.add("b")
        setm.add("c")
        setm.add("d")
        self.assertEqual(setm, OrderedSet(['b', 'c', 'd']))

    def test_discard(self):
        set1 = OrderedSet("abc")
        self.assertEqual(len(set1), 3)
        set1.discard("b")
        self.assertEqual(len(set1), 2)


class TestHeap(unittest.TestCase):
    def test_basic(self):
        heap = Heap(2)
        heap.add(4, "woof")
        heap.add(3, "meow")
        heap.add(10, "moo")
        self.assertEqual(len(heap), 2)
        self.assertEqual(heap.smallest(), [(4, "woof")])
        self.assertEqual(heap.largest(), [(10, "moo")])

    def test_order(self):
        h = Heap(3)
        h.append(time.clock(), "xz")
        h.append(time.clock(), "io")
        h.append(time.clock(), "zz")
        dropped = h.append(time.clock(), "zz")
        self.assertEqual(dropped[1], "xz")
        self.assertEqual(list(h), ["io", "zz", "zz"])
