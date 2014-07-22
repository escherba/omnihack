Pythonic containers for data analysis
===============================================================

Omnihack is a collection of miscellaneous containers that
make it easier to analyze data sets.

enumerator is an key-value mapping that maps keys to numeric
indices assigned in the order of first access.

::

    enum = enumerator()
    >>
    print enum["cat"]
    >> 0
    print enum["dog"]
    >> 1
    print enum["cat"]
    >> 0
    print len(enum)
    >> 2

UnionFind is a an algorithm for returning maintainig and retrieving
connected components in a graph. Example:

::

    uf = UnionFind()
    uf.union(0, 1)
    uf.union(2, 3)
    uf.union(3, 0)
    uf.union(4, 5)
    print uf.sets()
    >> [[0, 1, 2, 3], [4, 5]]
