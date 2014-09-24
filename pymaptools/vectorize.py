import collections


def doc(s):
    if hasattr(s, '__call__'):
        s = s.__doc__

    def f(g):
        g.__doc__ = s
        return g
    return f


class enumerator(collections.Mapping):
    """
    A simple vectorizer for text tokens

    >>> enum = enumerator()
    >>> enum["cat"]
    0
    >>> enum["dog"]
    1
    >>> enum["cat"]
    0
    >>> len(enum)
    2

    """

    def __init__(self):
        self.d = {}

    @doc(dict.__getitem__)
    def __getitem__(self, item):
        if item in self.d:
            return self.d[item]
        else:
            val = len(self.d)
            self.d[item] = val
            return val

    @doc(dict.__str__)
    def __str__(self):
        return str(self.d)

    @doc(dict.__iter__)
    def __iter__(self):
        return iter(self.d)

    @doc(dict.__len__)
    def __len__(self):
        return len(self.d)


del doc
