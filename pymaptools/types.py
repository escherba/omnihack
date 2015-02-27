class Struct(object):
    """An abstract class with namespace-like properties

    Note:

    collections.namedtuple is similar in concept but is too strict
    (requires all the keys every time you instantiate)

    bunch.Bunch object is very close to what we want, but it is not
    strict (it will not throw an error if we try to assign to it a
    a property it does not know about)

    >>> class Duck(Struct):
    ...     readonly_attrs = frozenset(["description"])
    ...     readwrite_attrs = frozenset(["vocalization", "locomotion"])
    >>> duck = Duck(description="a medium-size bird")
    >>> duck.vocalization
    >>> duck.locomotion = "walk, swim, fly"
    >>> duck.vocalization = "quack"
    >>> duck.description = "an ostrich"
    Traceback (most recent call last):
    ...
    AttributeError: Attribute 'description' of Duck instance is read-only
    >>> duck.engine_type
    Traceback (most recent call last):
    ...
    AttributeError: 'Duck' object has no attribute 'engine_type'
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
    readwrite_attrs = frozenset()
    readonly_attrs = frozenset()

    @classmethod
    def fromDict(cls, entries):
        return cls(**entries)

    def toDict(self):
        return dict(self.__dict__)

    def __init__(self, **entries):
        self_dict = self.__dict__
        readwrite_attrs = self.readwrite_attrs
        readonly_attrs = self.readonly_attrs
        for name, value in entries.iteritems():
            if (name in readwrite_attrs) or (name in readonly_attrs):
                self_dict[name] = value
            else:
                raise AttributeError(
                    "{} instance has no attribute '{}'".format(
                        self.__class__.__name__, name))

    def __setattr__(self, name, value):
        """Set an attribute

        Note that this also creates an attribute if one does not exist
        but is listed among the readwrite attribute names
        """
        if name in self.readwrite_attrs:
            self.__dict__[name] = value
        elif name in self.readonly_attrs:
            raise AttributeError(
                "Attribute '{}' of {} instance is read-only".format(
                    name, self.__class__.__name__))
        else:
            raise AttributeError(
                "{} instance has no attribute '{}'".format(
                    self.__class__.__name__, name))

    def __getattr__(self, name):
        if name in self.readwrite_attrs or name in self.readonly_attrs:
            return None
        else:
            raise AttributeError(
                "'{}' object has no attribute '{}'".format(
                    self.__class__.__name__, name))
