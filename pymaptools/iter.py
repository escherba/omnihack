"""
Many definitions here are from https://docs.python.org/2/library/itertools.html
"""
import collections
import operator
import random
from itertools import islice, imap, chain, starmap, ifilterfalse, count, \
    repeat, izip, izip_longest, groupby, cycle, tee, combinations


def isiterable(obj):
    """
    Are we being asked to look up a list of things, instead of a single thing?
    We check for the `__iter__` attribute so that this can cover types that
    don't have to be known by this module, such as NumPy arrays.

    Strings, however, should be considered as atomic values to look up, not
    iterables.

    We don't need to check for the Python 2 `unicode` type, because it doesn't
    have an `__iter__` attribute anyway.

    This method was written by Luminoso Technologies
        https://github.com/LuminosoInsight/ordered-set
    """
    return hasattr(obj, '__iter__') and not isinstance(obj, str)


def ismonotonic(oper, iterable):
    """Check whether values in iterable are monotonic according to operator

    http://en.wikipedia.org/wiki/Monotonic_function

    >>> ismonotonic(operator.le, [1, 2, 3, 3])
    True
    >>> ismonotonic(operator.le, ["a", "b", "aa"])
    False
    >>> ismonotonic(operator.ge, [4, 2])
    True
    >>> ismonotonic(operator.ge, [2, 4])
    False
    """
    return all(oper(x, y) for x, y in izip(iterable, iterable[1:]))


def pyramid_slices(lst):
    """Treat input list as a hierarchical path and return all subpaths

    >>> list(pyramid_slices([1, 2, 3]))
    [[1], [1, 2], [1, 2, 3]]
    """
    for i in xrange(len(lst)):
        yield lst[:i + 1]


def shinglify(iterable, span, skip=0):
    """Extract shingles from an iterable

    :param iterable: Iterable
    :type iterable: collections.Iterable
    :param span: shingle span
    :type span: int
    :param skip: How many words to skip
    :type skip: int
    :returns: sequence of tuples (shingles)
    :rtype : list

    >>> shingles = list(shinglify("abracadabra", 5, skip=1))
    >>> len(shingles)
    7
    >>> ('d', 'b', 'a') in shingles
    True

    Must return a single shingle when span > len(tokens)
    >>> list(shinglify("abc", 4))
    [('a', 'b', 'c')]

    Must return an empty list when span=0
    >>> list(shinglify("abc", 0))
    []

    Must return the last pair
    >>> list(shinglify("abcde", 4, skip=1))
    [('a', 'c'), ('b', 'd'), ('c', 'e')]

    Must also skip tokens when span > len(tokens)
    >>> list(shinglify("abc", 4, skip=1))
    [('a', 'c')]

    """
    tokens = iterable if isinstance(iterable, list) else list(iterable)
    if len(tokens) >= span:
        return izip(*nskip(skip, (tokens[i:] for i in xrange(span))))
    else:
        return [tuple(nskip(skip, tokens))]


def inverse_kvals(mapping):
    """Inverse a sparse-value dense-key dict form where values are assumed to be lists

    Resulting dict is sparse-key, dense-value

    >>> {k: v for k, v in inverse_kvals({"a": [1, 2], "b": [3]})}
    {1: 'a', 2: 'a', 3: 'b'}
    """
    for key, vals in mapping.iteritems():
        for val in vals:
            yield val, key


def nskip(n, iterable):
    """Skip some elements from an iterable

    :param n: How many items to skip
    :type n: int
    :param iterable: Iterable
    :type iterable: collections.Iterable
    :returns: sequence with skipped items
    :rtype: generator

    >>> list(nskip(2, "abcdefg"))
    ['a', 'd', 'g']
    >>> list(nskip(5, "abc"))
    ['a']
    """
    n_1 = n + 1
    return (v for i, v in enumerate(iterable) if not i % n_1)


def ntuples(n, iterable):
    """Tuplify an iterable

    :param n: Tuple size
    :type n: int
    :param iterable: Iterable
    :type iterable: collections.Iterable
    :returns: iterable of tuples
    :rtype: itertools.izip

    >>> list(ntuples(2, "abcde"))
    [('a', 'b'), ('c', 'd')]
    >>> list(ntuples(2, "abcd"))
    [('a', 'b'), ('c', 'd')]
    """
    return izip(*[iterable[i::n] for i in xrange(n)])


def take(n, iterable):
    """Return first n items of the iterable as a list

    >>> take(2, [1, 2, 3])
    [1, 2]
    """
    return list(islice(iterable, n))


def tabulate(function, start=0):
    """Return function(0), function(1), ...

    >>> foo = tabulate(lambda x: x + 5, 10)
    >>> foo.next()
    15
    """
    return imap(function, count(start))


def consume(iterator, n):
    """Advance the iterator n-steps ahead. If n is none, consume entirely

    >>> myiter = count(5)
    >>> consume(myiter, 4)
    >>> myiter.next()
    9

    >>> myiter = iter([1, 2, 3])
    >>> consume(myiter, None)
    >>> list(myiter)
    []
    """
    # Use functions that consume iterators at C speed.
    if n is None:
        # feed the entire iterator into a zero-length deque
        collections.deque(iterator, maxlen=0)
    else:
        # advance to the empty slice starting at position n
        next(islice(iterator, n, n), None)


def nth(iterable, n, default=None):
    """Returns the nth item or a default value

    >>> nth(count(5), 6)
    11
    """
    return next(islice(iterable, n, None), default)


def quantify(iterable, pred=bool):
    """Sum predicate output over a sequence

    Example: count odd numbers
    >>> quantify([1, 2, 3, 4, 5], pred=lambda x: x % 2)
    3
    """
    return sum(imap(pred, iterable))


def padnone(iterable):
    """Returns the sequence elements and then returns None indefinitely.

    Useful for emulating the behavior of the built-in map() function.

    >>> take(4, padnone([1,2,3]))
    [1, 2, 3, None]
    """
    return chain(iterable, repeat(None))


def ncycles(iterable, n):
    """Returns the sequence elements n times

    >>> list(ncycles([1,2,3], 2))
    [1, 2, 3, 1, 2, 3]
    """
    return chain.from_iterable(repeat(tuple(iterable), n))


def dotproduct(vec1, vec2):
    """Return a dot product of two vectors

    >>> dotproduct([1, 2, 3], [2, 3, 4])
    20
    """
    return sum(imap(operator.mul, vec1, vec2))


def flatten(iterable):
    """Flatten one level of nesting

    :param iterable: a list of lists
    :type iterable: collections.Iterable

    >>> list(flatten([[1,2,3],[3,4,5]]))
    [1, 2, 3, 3, 4, 5]
    """
    return chain.from_iterable(iterable)


def repeatfunc(func, times=None, *args):
    """Repeat calls to func with specified arguments.

    Example: repeatfunc(random.random)
    """
    if times is None:
        return starmap(func, repeat(args))
    return starmap(func, repeat(args, times))


def pairwise(iterable):
    """
    >>> list(pairwise([1,2,3]))
    [(1, 2), (2, 3)]
    """
    a, b = tee(iterable)
    next(b, None)
    return izip(a, b)


def grouper(iterable, n, fillvalue=None):
    """Collect data into fixed-length chunks or blocks

    >>> list(grouper('ABCDEFG', 3, 'x'))
    [('A', 'B', 'C'), ('D', 'E', 'F'), ('G', 'x', 'x')]
    """
    args = [iter(iterable)] * n
    return izip_longest(fillvalue=fillvalue, *args)


def roundrobin(*iterables):
    """
    Recipe credited to George Sakkis

    >>> list(roundrobin('ABC', 'D', 'EF'))
    ['A', 'D', 'E', 'B', 'F', 'C']
    """
    pending = len(iterables)
    funs = cycle(iter(it).next for it in iterables)
    while pending:
        try:
            for fun in funs:
                yield fun()
        except StopIteration:
            pending -= 1
            funs = cycle(islice(funs, pending))


def powerset(iterable):
    """ Return a power set of an iterable

    >>> list(powerset([1,2,3]))
    [(), (1,), (2,), (3,), (1, 2), (1, 3), (2, 3), (1, 2, 3)]
    """
    s = iterable if isinstance(iterable, list) else list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))


def unique_everseen(iterable, key=None):
    """ List unique elements, preserving order. Remember all elements ever seen

    >>> list(unique_everseen('AAAABBBCCDAABBB'))
    ['A', 'B', 'C', 'D']
    >>> list(unique_everseen('ABBCcAD', str.lower))
    ['A', 'B', 'C', 'D']
    """
    seen = set()
    seen_add = seen.add
    if key is None:
        for element in ifilterfalse(seen.__contains__, iterable):
            seen_add(element)
            yield element
    else:
        for element in iterable:
            k = key(element)
            if k not in seen:
                seen_add(k)
                yield element


def unique_justseen(iterable, key=None):
    """List unique elements, preserving order.
    Remember only the element just seen

    >>> list(unique_justseen('AAAABBBCCDAABBB'))
    ['A', 'B', 'C', 'D', 'A', 'B']
    >>> list(unique_justseen('ABBCcAD', str.lower))
    ['A', 'B', 'C', 'A', 'D']
    """
    return imap(next, imap(operator.itemgetter(1), groupby(iterable, key)))


def iter_except(func, exception, first=None):
    """Call a function repeatedly until an exception is raised.

    Converts a call-until-exception interface to an iterator interface.
    Like __builtin__.iter(func, sentinel) but uses an exception instead
    of a sentinel to end the loop.

    Examples:
        bsddbiter = iter_except(db.next, bsddb.error, db.first)
        heapiter = iter_except(functools.partial(heappop, h), IndexError)
        dictiter = iter_except(d.popitem, KeyError)
        dequeiter = iter_except(d.popleft, IndexError)
        queueiter = iter_except(q.get_nowait, Queue.Empty)
        setiter = iter_except(s.pop, KeyError)

    """
    try:
        if first is not None:
            yield first()
        while 1:
            yield func()
    except exception:
        pass


def first_nonempty(iterable):
    """Return first value from iterable not equal to None

    after http://stackoverflow.com/a/18533669/597371
    """
    try:
        return next(item for item in iterable if item is not None)
    except StopIteration:
        pass


def random_product(*args, **kwds):
    """Random selection from itertools.product(*args, **kwds)"""
    pools = map(tuple, args) * kwds.get('repeat', 1)
    return tuple(random.choice(pool) for pool in pools)


def random_permutation(iterable, r=None):
    """Random selection from itertools.permutations()
    """
    pool = tuple(iterable)
    r = len(pool) if r is None else r
    return tuple(random.sample(pool, r))


def random_combination(iterable, r):
    """Random selection from itertools.combinations()
    """
    pool = tuple(iterable)
    num = len(pool)
    indices = sorted(random.sample(xrange(num), r))
    return tuple(pool[i] for i in indices)


def random_combination_with_replacement(iterable, r):
    """Random selection from itertools.combinations_with_replacement()
    """
    pool = tuple(iterable)
    num = len(pool)
    indices = sorted(random.randrange(num) for i in xrange(r))
    return tuple(pool[i] for i in indices)


def tee_lookahead(t, i):
    """Inspect the i-th upcomping value from a tee object
       while leaving the tee object at its current position.

    Raise an IndexError if the underlying iterator doesn't
    have enough values.

    """
    for value in islice(t.__copy__(), i, None):
        return value
    raise IndexError(i)
