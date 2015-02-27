from pymaptools import uniq

"""
the get_class_attrs and get_object_attrs methods below
are based on http://stackoverflow.com/a/10313703/597371
"""


def get_class_attrs(klass):
    """Get attributes of a class
    """
    ret = dir(klass)
    if hasattr(klass, '__bases__'):
        for base in klass.__bases__:
            ret.extend(get_class_attrs(base))
    return ret


def get_object_attrs(obj):
    """Get attributes of an object
    """
    ret = dir(obj)
    if hasattr(obj, '__class__'):
        ret.append('__class__')
        ret.extend(get_class_attrs(obj.__class__))
    return list(uniq(ret))


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
