import unittest
from pymaptools.graph import Bigraph, Graph


def makeSetPair(graph):
    return (graph.U, graph.V)


def normalize_paired_sets(paired_sets):
    for L, R in paired_sets:
        yield tuple(sorted(L)), tuple(sorted(R))


class TestGraph(unittest.TestCase):

    def test_bigraph1(self):
        g = Bigraph()
        g.add_clique(([1, 2, 3], [-1, -2, -3]))
        g.add_clique(([4], [-4, -5]))
        g.add_clique(([5], [-5, -6]))
        g.add_edge(10, 20)
        g.add_edge(30, 20)
        g.add_edge(30, 40)
        clique_list = list(g.find_cliques())
        self.assertEqual(6, len(clique_list))
        cliques = set(normalize_paired_sets(clique_list))
        self.assertSetEqual(set([
            ((30,),     (20, 40)),
            ((10, 30),  (20,)),
            ((1, 2, 3), (-3, -2, -1)),
            ((5,),      (-6, -5)),
            ((4, 5),    (-5,)),
            ((4,),      (-5, -4)),
        ]), cliques)
        component_list = map(makeSetPair, g.find_connected_components())
        self.assertEqual(3, len(component_list))
        components = set(normalize_paired_sets(component_list))
        self.assertSetEqual(set([
            ((1, 2, 3), (-3, -2, -1)),
            ((4, 5),    (-6, -5, -4)),
            ((10, 30),  (20, 40))
        ]), components)

    def test_bigraph1a(self):
        g = Bigraph()
        g.add_clique(([1, 2, 3], [-1, -2, -3]))
        g.add_clique(([4], [-4, -5]))
        g.add_clique(([5], [-5, -6]))
        g.add_edge(10, 20)
        g.add_edge(30, 20)
        g.add_edge(30, 40)
        g.add_edge(4, -1)
        component_list = map(makeSetPair, g.find_connected_components())
        self.assertEqual(2, len(component_list))
        components = set(normalize_paired_sets(component_list))
        self.assertSetEqual(set([
            ((1, 2, 3, 4, 5), (-6, -5, -4, -3, -2, -1)),
            ((10, 30),        (20, 40))
        ]), components)

    def test_bigraph1b(self):
        g = Bigraph()
        g.add_clique(([1, 2, 3], [-1, -2, -3]))
        h = Bigraph(g)
        g.add_clique(([4], [-4, -5]))
        g.add_clique(([5], [-5, -6]))
        g.add_edge(4, -1)
        h.add_edge(2, 100, weight=14)
        h.add_edge(5, -5, weight=10)
        j = g & h
        clique_list = list(j.find_cliques())
        self.assertEqual(2, len(clique_list))
        cliques = set(normalize_paired_sets(clique_list))
        self.assertSetEqual(set([
            ((1, 2, 3), (-3, -2, -1)),
            ((5,), (-5,))
        ]), cliques)

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

        clique_list = list(g.find_cliques())
        self.assertEqual(2, len(clique_list))
        cliques = set(normalize_paired_sets(clique_list))
        self.assertSetEqual(set([
            (('u1', 'u3'), ('v1', 'v2')),
            (('u1', 'u2', 'u3'), ('v2',))
        ]), cliques)

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
