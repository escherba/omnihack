omnihack: a collection of Pythonic containers
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


