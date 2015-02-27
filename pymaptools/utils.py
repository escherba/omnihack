import collections
import uuid
import sys
from copy import deepcopy
from contextlib import contextmanager


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


def hasmethod(obj, method):
    """check whether object has a method
    """
    return hasattr(obj, method) and callable(getattr(obj, method))


def iter_methods(obj, names):
    """Return all methods from list of names supported by object

    >>> from pymaptools.iter import first_nonempty
    >>> class Foo(object):
    ...     def bar(self):
    ...         return "bar called"
    >>> foo = Foo()
    >>> method = first_nonempty(iter_methods(foo, ['missing', 'bar']))
    >>> hasmethod(foo, method.__name__)
    True
    >>> method()
    'bar called'
    """
    for method_name in names:
        if hasattr(obj, method_name):
            method = getattr(obj, method_name)
            if callable(method):
                yield method


def uuid1_to_posix(uuid1):
    """Convert a UUID1 timestamp to a standard POSIX timestamp

    >>> uuid1_to_posix("d64736cf-5bfa-11e4-a292-542696da2c01")
    1414209362.290043
    """
    uuid1 = uuid.UUID(uuid1)
    if uuid1.version != 1:
        raise ValueError('only applies to UUID type 1')
    return (uuid1.time - 0x01b21dd213814000) / 1e7


def deepupdate(dest, source):
    """Recursively update one dict with contents of another

    :param dest: mapping being updated
    :type dest: dict
    :param source: mapping to update with
    :type source: collections.Mapping
    :return: updated mapping
    :rtype: dict
    """
    for key, value in source.iteritems():
        dest[key] = deepupdate(dest.get(key, {}), value) \
            if isinstance(value, collections.Mapping) \
            else value
    return dest


def override(parent, child):
    """Inherit child from parent and return a new object
    """
    return deepupdate(deepcopy(parent), child)


@contextmanager
def empty_context(*args, **kwargs):
    """Generic empty context wrapper
    """
    yield None


@contextmanager
def joint_context(*args):
    """Generic empty context wrapper

    Allows constructions like:
    with join_context(open("filename.txt", "r")) as fhandle:
    with join_context(open("file1.txt", "r"), open("file2.txt", "r")) as (fh1, fh2):
    """
    try:
        yield args[0] if len(args) == 1 else args
    finally:
        for arg in args:
            if arg is not sys.stdout:
                arg.close()
