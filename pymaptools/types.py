class Struct(object):
    """An abstract class with namespace-like properties

    Note:

    collections.namedtuple is similar in concept but is too strict
    (requires all the keys every time you instantiate)

    bunch.Bunch object is very close to what we want, but it is not
    strict (it will not throw an error if we try to assign to it a
    a property it does not know about)

    >>> class Duck(Struct):
    ...     supported_attrs = frozenset(["appearance", "vocalization", "locomotion"])
    >>> duck = Duck(appearance="a medium-size bird")
    >>> duck.vocalization
    >>> duck.engine_type
    Traceback (most recent call last):
    ...
    AttributeError: 'Duck' object has no attribute 'engine_type'
    >>> duck.locomotion = "walk, swim, fly"
    >>> duck.vocalization = "quack"
    >>> duck.laden_speed = "40 mph"
    Traceback (most recent call last):
    ...
    AttributeError: Duck instance has no attribute 'laden_speed'
    >>> duck.toDict()['vocalization']
    'quack'
    >>> another_duck = Duck.fromDict(duck.toDict())
    >>> another_duck.toDict()['locomotion']
    'walk, swim, fly'
    >>> another_duck.locomotion
    'walk, swim, fly'

    """
    supported_attrs = frozenset()

    @classmethod
    def fromDict(cls, entries):
        return cls(**entries)

    def toDict(self):
        return dict(self.__dict__)

    def _set_attr(self, name, value):
        """Creates an attribute if one does not exist
        but is listed among the supported attribute names
        """
        if name in self.supported_attrs:
            self.__dict__[name] = value
        else:
            raise AttributeError(
                "{} instance has no attribute '{}'".format(
                    self.__class__.__name__, name))

    def __init__(self, **entries):
        for name, value in entries.iteritems():
            self._set_attr(name, value)

    def __setattr__(self, name, value):
        self._set_attr(name, value)

    def __getattr__(self, name):
        if name in self.supported_attrs:
            return None
        else:
            raise AttributeError(
                "'{}' object has no attribute '{}'".format(
                    self.__class__.__name__, name))
