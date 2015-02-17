class Struct(object):
    """An abstract class with namespace-like properties

    Note:

    collections.namedtuple is similar in concept but is too strict
    (requires all the keys every time you instantiate)

    bunch.Bunch object is very close to what we want, but it is not
    strict (it will not throw an error if we try to assign to it a
    a property it does not know about)

    >>> class Duck(Struct):
    ...     supported_attrs = frozenset(["appearance", "sound", "locomotion"])
    >>> duck = Duck(appearance="a medium-size bird")
    >>> duck.locomotion = "walk, swim"
    >>> duck.sound = "quack"
    >>> duck.laden_speed = "40 mph"
    Traceback (most recent call last):
    ...
    TypeError: Duck instance has no attribute 'laden_speed'
    >>> duck.toDict()
    {'sound': 'quack', 'locomotion': 'walk, swim', 'appearance': 'a medium-size bird'}
    >>> another_duck = Duck.fromDict(duck.toDict())
    >>> another_duck.toDict()
    {'sound': 'quack', 'locomotion': 'walk, swim', 'appearance': 'a medium-size bird'}
    >>> another_duck.locomotion
    'walk, swim'
    """
    supported_attrs = frozenset()

    @classmethod
    def fromDict(cls, entries):
        return cls(**entries)

    def toDict(self):
        return dict(self.__dict__)

    def _set_attr(self, key, val):
        """Creates an attribute if one does not exist
        but is listed among the supported attribute names
        """
        if key in self.supported_attrs:
            self.__dict__[key] = val
        else:
            raise TypeError("{} instance has no attribute '{}'"
                            .format(self.__class__.__name__, key))

    def __init__(self, **entries):
        for key, val in entries.iteritems():
            self._set_attr(key, val)

    def __setattr__(self, key, val):
        self._set_attr(key, val)
