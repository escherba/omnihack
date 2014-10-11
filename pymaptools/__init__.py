__version__ = '0.0.8'

from vectorize import enumerator
from unionfind import UnionFind

from functools import partial
from funcy import compose
from itertools import imap


def amap(f, g):
    """Lift a scalar transformer f into an iterable

    :param f: transformer of type a -> b where a, b are scalars
    :type f: function
    :param g: mapper of type L x (returns an iterator)
    :type g: function
    :return: an iterable over domain of g with f mapped over range of g
    :rtype: function

    >>> def foo(x):
    ...     for i in range(x):
    ...         yield i
    >>> bar = amap(lambda x: x + 10, foo)
    >>> list(bar(5))
    [10, 11, 12, 13, 14]

    """
    return compose(partial(imap, f), g)
