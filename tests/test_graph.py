import unittest
from pymaptools.graph import Bigraph, Graph


def makeSetPair(graph):
    return (graph.U, graph.V)


class TestGraph(unittest.TestCase):

    def assertSetPairsEqual(self, seq1, seq2):
        """Small extension to unittest to test for equality of set pairs

        Also tests whether one of the iterables is longer than the other
        """
        iter1 = iter(seq1)
        iter2 = iter(seq2)
        for set1, set2 in zip(iter1, iter2):
            self.assertSetEqual(set(set1), set(set2))
        self.assertRaises(StopIteration, iter1.next)
        self.assertRaises(StopIteration, iter2.next)

    def test_bigraph1(self):
        g = Bigraph()
        g.add_biclique([1, 2, 3], [-1, -2, -3])
        g.add_biclique([4], [-4, -5])
        g.add_biclique([5], [-5, -6])
        g.add_edge(10, 20)
        g.add_edge(30, 20)
        g.add_edge(30, 40)
        cliques = list(g.find_cliques())
        self.assertEqual(6, len(cliques))
        self.assertSetPairsEqual(([30], [40, 20]), cliques[0])
        self.assertSetPairsEqual(([10, 30], [20]), cliques[1])
        self.assertSetPairsEqual(([1, 2, 3], [-1, -2, -3]), cliques[2])
        self.assertSetPairsEqual(([5], [-6, -5]), cliques[3])
        self.assertSetPairsEqual(([4, 5], [-5]), cliques[4])
        self.assertSetPairsEqual(([4], [-5, -4]), cliques[5])
        components = list(g.find_connected_components())
        self.assertEqual(3, len(components))
        self.assertSetPairsEqual(([1, 2, 3], [-1, -3, -2]), makeSetPair(components[0]))
        self.assertSetPairsEqual(([4, 5], [-6, -5, -4]), makeSetPair(components[1]))
        self.assertSetPairsEqual(([10, 30], [40, 20]), makeSetPair(components[2]))

    def test_bigraph2(self):
        g = Bigraph()
        g.add_biclique([1, 2, 3], [-1, -2, -3])
        g.add_biclique([4], [-4, -5])
        g.add_biclique([5], [-5, -6])
        g.add_edge(10, 20)
        g.add_edge(30, 20)
        g.add_edge(30, 40)
        g.add_edge(4, -1)
        components = list(g.find_connected_components())
        self.assertEqual(2, len(components))
        self.assertSetPairsEqual(([1, 2, 3, 4, 5], [-2, -6, -5, -4, -3, -1]),
                                 makeSetPair(components[0]))
        self.assertSetPairsEqual(([10, 30], [40, 20]),
                                 makeSetPair(components[1]))

    def test_bigraph3(self):
        """Simple bigraph given in Fig. 2 of MBEA paper
        """
        g = Bigraph()
        g.add_edge("u3", "v2")
        g.add_edge("u3", "v1")
        g.add_edge("u2", "v2")
        g.add_edge("u1", "v1")
        g.add_edge("u1", "v2")

        # there should be a single connected component
        components = list(g.find_connected_components())
        self.assertEqual(1, len(components))
        cliques = list(g.find_cliques())
        self.assertEqual(2, len(cliques))
        self.assertSetPairsEqual((set(['u1', 'u3']), set(['v1', 'v2'])), cliques[0])
        self.assertSetPairsEqual((set(['u1', 'u3', 'u2']), set(['v2'])), cliques[1])

    def test_graph(self):
        a = Graph()
        a.add_edge(1, 5)
        a.add_edge(1, 2)
        a.add_edge(2, 5)
        a.add_edge(2, 3)
        a.add_edge(3, 4)
        a.add_edge(4, 5)
        a.add_edge(10, 20)
        cliques = list(a.find_cliques())
        self.assertEqual(1, len(cliques))
        self.assertSetEqual(set([1, 2, 5]), cliques[0])
        components = list(a.find_connected_components())
        self.assertEqual(2, len(components))
        self.assertSetEqual(set([1, 2, 3, 4, 5]), set(components[0].V))
        self.assertSetEqual(set([10, 20]), set(components[1].V))

        b = Graph()
        b.add_edge(3, 7)
        b.add_edge(7, 8)
        b.add_edge(4, 8)
        b.add_edge(4, 3)
        cliques = list(b.find_cliques())
        self.assertEqual(0, len(cliques))
        components = list(b.find_connected_components())
        self.assertEqual(1, len(components))
        self.assertSetEqual(set([3, 4, 8, 7]), set(components[0].V))

        a_and_b = a & b
        components = list(a_and_b.find_connected_components())
        self.assertEqual(1, len(components))
        self.assertSetEqual(set([3, 4]), set(components[0].V))
        cliques = list(a_and_b.find_cliques())
        self.assertEqual(0, len(cliques))

        a_sub_b = a - b
        components = list(a_sub_b.find_connected_components())
        self.assertEqual(2, len(components))
        self.assertSetEqual(set([1, 2, 3, 4, 5]), set(components[0].V))
        self.assertSetEqual(set([10, 20]), set(components[1].V))
        cliques = list(a_sub_b.find_cliques())
        self.assertEqual(1, len(cliques))
        self.assertSetEqual(set([1, 2, 5]), cliques[0])

        b_sub_a = b - a
        components = list(b_sub_a.find_connected_components())
        self.assertEqual(1, len(components))
        self.assertSetEqual(set([3, 4, 7, 8]), set(components[0].V))
        cliques = list(b_sub_a.find_cliques())
        self.assertEqual(0, len(cliques))

        a_or_b = a | b
        components = list(a_or_b.find_connected_components())
        self.assertEqual(2, len(components))
        self.assertSetEqual(set([1, 2, 3, 4, 5, 7, 8]), set(components[0].V))
        self.assertSetEqual(set([10, 20]), set(components[1].V))
        cliques = list(a_or_b.find_cliques())
        self.assertEqual(1, len(cliques))
        self.assertSetEqual(set([1, 2, 5]), cliques[0])

        # test some properties
        # (a - b) | (a & b) | (b - a) == a | b
        #a_or_b_alt = a_sub_b | a_and_b | b_sub_a
        #self.assertEqual(a_or_b, a_or_b_alt)

        # test commutative OR
        # a | b == b | a
        b_or_a = b | a
        self.assertEqual(a_or_b, b_or_a)

        # test commutative AND
        # a & b == b & a
        b_and_a = b & a
        self.assertEqual(a_and_b, b_and_a)


if __name__ == "__main__":
    unittest.main()
