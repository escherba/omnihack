import collections
from cyordereddict import OrderedDict
from heapq import heappush, heapreplace, nsmallest, nlargest, heappop
from pymaptools.utils import isiterable


SLICE_ALL = slice(None)


class OrderedSet(collections.MutableSet, collections.Sequence):
    """
    An OrderedSet is a custom MutableSet that remembers its order, so that
    every entry has an index that can be looked up.

    Based on version written by Luminoso Technologies:
        https://github.com/LuminosoInsight/ordered-set

    Unlike that implementation, this class uses OrderedDict as storage
    and supports key removal. We drop support for indexing, and add support
    for fixed-size sets with maxlen parameter.

    With a small modification, this class can be made into an LRU cache.
    """
    def __init__(self, iterable=None, maxlen=None):
        self._mapping = OrderedDict()
        self._maxlen = maxlen
        if iterable is not None:
            self |= iterable

    def __len__(self):
        return len(self._mapping)

    def __getitem__(self, index):
        """
        Get the item at a given index.

        If `index` is a slice, you will get back that slice of items. If it's
        the slice [:], exactly the same object is returned. (If you want an
        independent copy of an OrderedSet, use `OrderedSet.copy()`.)

        If `index` is an iterable, you'll get the OrderedSet of items
        corresponding to those indices. This is similar to NumPy's
        "fancy indexing".
        """
        if index == SLICE_ALL:
            return self
        elif hasattr(index, '__index__') or isinstance(index, slice):
            result = self._mapping.keys()[index]
            if isinstance(result, list):
                return OrderedSet(result)
            else:
                return result
        elif isiterable(index):
            keys = self._mapping.keys()
            return OrderedSet([keys[i] for i in index])
        else:
            raise TypeError("Don't know how to index an OrderedSet by %r" % index)

    def copy(self):
        return OrderedSet(self)

    def __getstate__(self):
        if len(self) == 0:
            # The state can't be an empty list.
            # We need to return a truthy value, or else __setstate__ won't be run.
            #
            # This could have been done more gracefully by always putting the state
            # in a tuple, but this way is backwards- and forwards- compatible with
            # previous versions of OrderedSet.
            return (None,)
        else:
            return list(self)

    def __setstate__(self, state):
        if state == (None,):
            self.__init__([])
        else:
            self.__init__(state)

    def __contains__(self, key):
        return key in self._mapping

    def add(self, key):
        """
        Add `key` as an item to this OrderedSet, then return its index.

        If `key` is already in the OrderedSet, return the index it already
        had.
        """
        if key not in self._mapping:
            if self._maxlen is None or len(self._mapping) < self._maxlen:
                self._mapping[key] = 1
            else:
                self._mapping.popitem(last=False)
                self._mapping[key] = 1

    append = add

    def discard(self, key):
        del self._mapping[key]

    def __iter__(self):
        return self._mapping.iterkeys()

    def __reversed__(self):
        return reversed(self._mapping.keys())

    def __repr__(self):
        if not self:
            return '%s()' % (self.__class__.__name__,)
        return '%s(%r)' % (self.__class__.__name__, list(self))

    def __eq__(self, other):
        if isinstance(other, OrderedSet):
            return len(self) == len(other) and \
                self._mapping.keys() == other._mapping.keys()
        try:
            other_as_set = set(other)
        except TypeError:
            # If `other` can't be converted into a set, it's not equal.
            return False
        else:
            return set(self) == other_as_set


class Heap(collections.Iterable):
    """Super-simple object-oriented interface for python's heap queue

    Allows one to easily maintain fixed-sized heaps

    >>> h = Heap(maxlen=2)
    >>> h.add(4, "woof")
    >>> h.add(3, "meow")
    >>> h.add(10, "moo")
    (3, 'meow')
    >>> list(h)
    ['woof', 'moo']
    >>> list(reversed(h))
    ['moo', 'woof']
    """

    def __init__(self, maxlen=None):
        """
        :param maxlen: maximum number of items in heap (no limit if None)
        :type maxlen: int
        """
        self._heap = []
        self._maxlen = maxlen

    def add(self, priority, item):
        """Place an item on the heap"""
        if self._maxlen is None or len(self._heap) < self._maxlen:
            return heappush(self._heap, (priority, item))
        elif self._maxlen > 0:
            return heapreplace(self._heap, (priority, item))

    append = add

    def __len__(self):
        """Return number of elements in the heap
        :rtype: int
        """
        return len(self._heap)

    def smallest(self, n=1):
        """same as heapq.nsmallest"""
        return nsmallest(n, self._heap)

    def largest(self, n=1):
        """same as heapq.nlargest"""
        return nlargest(n, self._heap)

    def __iter__(self):
        """iterate from smallest to largest"""
        return (v for _, v in nsmallest(len(self._heap), self._heap))

    def __reversed__(self):
        """iterate from largest to smallest"""
        return (v for _, v in nlargest(len(self._heap), self._heap))


class RangeQueue(object):
    """Rank objects according to consistently-spaced index

    Motivation: Sometimes an ordered stream of items becomes disordered (for example,
    due to several workers operating on it). In that case, one may still decide
    to return items in order (i.e. do not wait until all items are
    processed to start the sorting phase and instead finish in one pass).
    The idea is that the workers hopefully will not disorganize the list
    *too much* (i.e.  will not introduce *very* large distances between
    former neighboring items). If so, one may take adavantage of this partial
    order and try to return all items in order by caching n items (where n
    is hopefully a small number) untill all n items form a whole "run" without
    any lacking items in the middle and thus can be retrieved at once.

    >>> queue = RangeQueue()
    >>> queue.push(1, "a")
    >>> list(queue.retrieve())
    []
    >>> queue.push(0, "b")
    >>> queue.push(2, "c")
    >>> list(queue.retrieve())
    ['b', 'a', 'c']
    """
    def __init__(self, start=0, step=1):
        self._heap = []
        self._prev_idx = start - step
        self._step = step

    def push(self, idx, value):
        """
        :param idx: index of the item
        :type idx: int
        :param value: item value
        """
        heappush(self._heap, (idx, value))

    def retrieve(self):
        """
        :rtype: generator
        """
        heap = self._heap
        step = self._step
        while heap and nsmallest(1, heap)[0][0] == self._prev_idx + step:
            self._prev_idx, value = heappop(heap)
            yield value
