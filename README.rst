omnihack: a collection of Pythonic containers
===============================================================

Omnihack is a collection of miscellaneous containers that
make it easier to analyze data sets.

indexer is an key-value mapping that maps keys to numeric
indices assigned in the order of first access.

::

    idx = indexer()
    >>
    print idx["cat"]
    >> 0
    print idx["dog"]
    >> 1
    print idx["cat"]
    >> 0
    print len(idx)
    >> 2


