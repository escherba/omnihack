__version__ = '0.0.10'

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


def all_equal(xs):
    """check that all elements of a list are equal
    :param xs: a sequence of elements
    :type xs: list, str
    :rtype: bool

    >>> all_equal("aaa")
    True
    >>> all_equal("abc")
    False
    >>> all_equal(["a", "b"])
    False
    >>> all_equal([1] * 10)
    True
    """
    return not xs or xs.count(xs[0]) == len(xs)


def uniq(tokens):
    """Analog of UNIX command uniq

    :param tokens: an iterable of hashable tokens
    :type tokens: collections.Iterable
    :return: a generator of unique tokens
    :rtype: generator

    >>> list(uniq([1, 1, 2, 3, 2, 4]))
    [1, 2, 3, 4]
    """
    seen = set()
    for token in tokens:
        if token not in seen:
            yield token
            seen.add(token)


def uniq_replace(tokens, placeholder=None):
    """Same as uniq except replace duplicate tokens with placeholder

    :param tokens: an iterable of hashable tokens
    :type tokens: collections.Iterable
    :param placeholder: some object
    :type placeholder: object
    :return: a generator of unique tokens
    :rtype: generator

    >>> list(uniq_replace([1, 1, 2, 3, 2, 4], 'x'))
    [1, 'x', 2, 3, 'x', 4]
    """
    seen = set()
    for token in tokens:
        if token in seen:
            yield placeholder
        else:
            yield token
            seen.add(token)
