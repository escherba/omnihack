Tools and algorithms for data wrangling
=======================================

PyMapTools are a collection of miscellaneous containers that
make it easier to analyze data sets.

enumerator
----------

``enumerator`` is a key-value mapping that maps keys to numeric
indices assigned in the order of first access. You can use it to vectorize strings.

.. code-block:: python

    >>> from pymaptools.vectorize import enumerator
    ...
    >>> enum = enumerator()
    >>> enum["cat"]
    0
    >>> enum["dog"]
    1
    >>> enum["cat"]
    0
    >>> len(enum)
    2

UnionFind
---------

``UnionFind`` is an algorithm for creating, maintainig, and retrieving
disjoint clusters from a graph. An example:

.. code-block:: python

    >>> from pymaptools.unionfind import UnionFind
    ...
    >>> uf = UnionFind()
    >>> uf.union(0, 1)
    >>> uf.union(2, 3)
    >>> uf.union(3, 0)
    >>> uf.union(4, 5)
    >>> uf.sets()
    [[0, 1, 2, 3], [4, 5]]

Pipe and Step
-------------

``Pipe`` is a basic pipeline for processing data in sequence. You create pipes by composing ``Step`` instances (or any callables). ``Pipe`` makes extensive use of generators to make processing memory-efficient. A basic example:

.. code-block:: python

    >>> from pymaptools.pipeline import Pipe, Step
    ...
    >>> def deserialize(obj):
    ...     yield int(obj)
    ...
    >>> def square(obj):
    ...     yield obj * obj
    ...
    >>> class Sum(Step):
    ...     def __init__(self):
    ...         self.sum = 0
    ...     def __call__(self, obj):
    ...         self.sum += obj
    ...
    >>> sumsq = Pipe([deserialize, square, Sum()])
    >>> sumsq.run(["1", "2", "3"])
    >>> sumsq.steps[-1].sum
    14

A more complex example:

.. code-block:: python

    import json
    import sys
    from pymaptools.pipeline import Pipe, Step

    def deserialize(obj):
        """ demonstrate use of plain functions as callables
            demonstrate multiple outputs
        """
        try:
            array = json.loads(obj)["x"]
            for num in array:
                yield int(num)
        except:
            print "failed to deserialize `{}`".format(obj)

    def filter_even(obj):
        """ demonstrate that values can be dropped """
        if obj % 2 == 0:
            yield obj

    class Add(Step):
        """ demonstrate use of state """
        def __init__(self, value):
            self.value = value

        def __call__(self, obj):
            yield obj + self.value

    class MultiplyBy(Step):
        def __init__(self, value):
            self.value = value

        def __call__(self, obj):
            yield obj * self.value

    class Output(Step):
        """ demonstrate that we can use IO """
        def __init__(self, handle):
            self.handle = handle

        def __call__(self, obj):
            self.handle.write(str(obj) + "\n")


    # process a sequence of possible JSON strings
    input_seq = ['{"x":[0,-6,4]}', '{"x":[12]}', '{"x":[34]}', '{"x":[-9]}',
                "Ceci n'est pas une pipe", '{"x":[4]}']
    pipe = Pipe([
        deserialize,
        filter_even,
        Add(10),
        MultiplyBy(2),
        Output(sys.stdout)
    ])
    pipe.run(input_seq)

The output of the above is:

.. code-block:: python

    20
    8
    28
    44
    88
    failed to deserialize `Ceci n\'est pas une pipe`
    28
