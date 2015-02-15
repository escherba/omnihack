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
