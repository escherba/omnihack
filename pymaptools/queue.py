from heapq import heappush, heapreplace, nsmallest, nlargest


class Heap(object):
    """Super-simple object-oriented interface for python's heap queue

    Allows one to easily maintain fixed-sized heaps

    >>> h = Heap(nmax=2)
    >>> h.push("woof", 4)
    >>> h.push("meow", 3)
    >>> h.push("moo", 10)
    >>> h.snapshot()
    [(10, 'moo'), (4, 'woof')]
    """

    def __init__(self, nmax=None):
        """
        :param nmax: maximum number of items in heap (no limit if None)
        :type nmax: int
        """
        self._heap = []
        self._nmax = nmax

    def push(self, item, priority):
        """Place an item on the heap"""
        if self._nmax is None or len(self._heap) < self._nmax:
            heappush(self._heap, (priority, item))
        else:
            heapreplace(self._heap, (priority, item))

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

    def snapshot(self, nmax=None):
        """Return all items stored sorted in descending order
        :param nmax: limit output to this many objects (no limit if none)
        :type nmax: int
        :rtype: list
        """
        limit = len(self._heap) if nmax is None else nmax
        return nlargest(limit, self._heap)
