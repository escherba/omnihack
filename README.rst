Algorithms and data structures for data analysis
================================================

About this repo
---------------

PyMapTools are a collection of miscellaneous containers that
make it easier to analyze data sets.

enumerator
----------

``enumerator`` is a key-value mapping that maps keys to numeric
indices assigned in the order of first access. You can use it to vectorize strings.

.. code-block:: python

    from pymaptools.vectorize import enumerator

    enum = enumerator()
    print enum["cat"]
    >> 0
    print enum["dog"]
    >> 1
    print enum["cat"]
    >> 0
    print len(enum)
    >> 2

UnionFind
---------

``UnionFind`` is an algorithm for creating, maintainig, and retrieving
disjoint clusters from a graph. Example:

.. code-block:: python

    from pymaptools.unionfind import UnionFind

    uf = UnionFind()
    uf.union(0, 1)
    uf.union(2, 3)
    uf.union(3, 0)
    uf.union(4, 5)
    print uf.sets()
    >> [[0, 1, 2, 3], [4, 5]]

Pipe and Filter
---------------

``Pipe`` is basic pipeline for processing data in sequence. You create pipes by composing ``Filter`` instances (or any callables). ``Pipe`` makes heavy use of generators to make processing memory-efficient:

.. code-block:: python

    from pymaptools.pipeline import Filter, Pipe

    class FilterDeserialize(Filter):
        """
        deserialize data
        """
        def __call__(self, obj):
            try:
                yield int(obj)
            except ValueError:
                yield 0


    class FilterMap(Filter):
        def __call__(self, obj):
            """
            demonstrate that values can be dropped
            """
            if obj % 2 == 0:
                yield obj
                yield -obj


    class FilterAdd(Filter):
        """
        demonstrate use of state
        """
        def __init__(self, init_sum):
            self.total = init_sum

        def __call__(self, obj):
            self.total += obj
            if self.total < 100:
                yield obj + 10


    def filter_multiply(obj):
        """
        demonstrate the use of plain functions as callables
        """
        yield obj * 2


    class FilterOutput(Filter):
        """
        demonstarte that we can use IO
        """
        def __call__(self, obj):
            print obj


    # finally,
    input_seq = ["0", "1", "2", "3", "abracadabra", "4", "5", "6"]
    pipe = Pipe([
        FilterDeserialize(),
        FilterMap(),
        FilterAdd(0),
        filter_multiply,
        FilterOutput()
    ])
    pipe.run(input_seq)

    # outputs:
    >> 20
    >> 20
    >> 24
    >> 16
    >> 20
    >> 20
    >> 28
    >> 12
    >> 32
    >> 8
