import copy
from itertools import izip
from functools import partial
from collections import OrderedDict, Callable
from pymaptools.iter import iter_items, iter_vals


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
    >>> duck.to_dict()['vocalization']
    'quack'
    >>> another_duck = Duck.from_dict(duck.to_dict())
    >>> another_duck.to_dict()['locomotion']
    'walk, swim, fly'
    >>> another_duck.locomotion
    'walk, swim, fly'

    """
    readwrite_attrs = frozenset()
    readonly_attrs = frozenset()

    @classmethod
    def from_dict(cls, entries):
        return cls(**entries)

    def to_dict(self):
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


class DefaultOrderedDict(OrderedDict):
    """Ordered dict with default constructors

    Attribution: http://stackoverflow.com/a/6190500/562769
    """
    def __init__(self, default_factory=None, *a, **kw):
        if (default_factory is not None and
           not isinstance(default_factory, Callable)):
            raise TypeError('first argument must be callable')
        OrderedDict.__init__(self, *a, **kw)
        self.default_factory = default_factory

    def __getitem__(self, key):
        try:
            return OrderedDict.__getitem__(self, key)
        except KeyError:
            return self.__missing__(key)

    def __missing__(self, key):
        if self.default_factory is None:
            raise KeyError(key)
        self[key] = value = self.default_factory()
        return value

    def __reduce__(self):
        if self.default_factory is None:
            args = tuple()
        else:
            args = self.default_factory,
        return type(self), args, None, None, self.items()

    def copy(self):
        return self.__copy__()

    def __copy__(self):
        return type(self)(self.default_factory, self)

    def __deepcopy__(self, memo):
        return type(self)(self.default_factory,
                          copy.deepcopy(self.items()))


OrderedCounter = partial(DefaultOrderedDict, int)


class TableOfCounts(object):

    """
    Example:

    >>> table1 = TableOfCounts(rows=[(1, 5), (4, 6)])
    >>> table1.grand_total
    16
    >>> table2 = TableOfCounts(cols=[(0, 0), (45, 0)])
    >>> table2.grand_total
    45
    >>> table2.col_totals.values()
    [0, 45]
    """
    # TODO: use one of Scipy's sparse matrix representations instead of
    # a dict of dicts

    def __init__(self, rows=None, cols=None,
                 row_totals=None, col_totals=None, grand_total=None):
        self.rows_ = rows
        self.cols_ = cols
        self.row_totals_ = row_totals
        self.col_totals_ = col_totals
        self.grand_total_ = grand_total

    @property
    def rows(self):
        rows_ = self.rows_
        if rows_ is None:
            rows_ = self.rows_ = DefaultOrderedDict(OrderedCounter)
            for cid, col in iter_items(self.cols_):
                for rid, cell in iter_items(col):
                    rows_[rid][cid] = cell
        return rows_

    @property
    def cols(self):
        cols_ = self.cols_
        if cols_ is None:
            cols_ = self.cols_ = DefaultOrderedDict(OrderedCounter)
            for rid, row in iter_items(self.rows_):
                for cid, cell in iter_items(row):
                    cols_[cid][rid] = cell
        return cols_

    @property
    def row_totals(self):
        row_totals_ = self.row_totals_
        if row_totals_ is None:
            row_totals_ = self.row_totals_ = OrderedCounter()
            for rid, row in iter_items(self.rows):
                row_totals_[rid] = sum(iter_vals(row))
        return row_totals_

    @property
    def col_totals(self):
        col_totals_ = self.col_totals_
        if col_totals_ is None:
            col_totals_ = self.cow_totals_ = OrderedCounter()
            for rid, col in iter_items(self.cols):
                col_totals_[rid] = sum(iter_vals(col))
        return col_totals_

    @property
    def grand_total(self):
        grand_total_ = self.grand_total_
        if grand_total_ is None:
            grand_total_ = self.grand_total_ = sum(self.iter_row_totals())
        return grand_total_

    @classmethod
    def from_labels(cls, labels_true, labels_pred):
        rows = DefaultOrderedDict(OrderedCounter)
        cols = DefaultOrderedDict(OrderedCounter)
        row_totals = OrderedCounter()
        col_totals = OrderedCounter()
        grand_total = 0
        for c, k in izip(labels_true, labels_pred):
            rows[c][k] += 1
            cols[k][c] += 1
            row_totals[c] += 1
            col_totals[k] += 1
            grand_total += 1
        return cls(rows=rows, cols=cols, row_totals=row_totals,
                   col_totals=col_totals, grand_total=grand_total)

    def iter_cells_with_indices(self):
        for ri, row in iter_items(self.rows):
            for ci, cell in iter_items(row):
                yield ri, ci, cell

    def iter_cells_with_margins(self):
        col_totals = self.col_totals
        row_totals = self.row_totals
        for ri, row in iter_items(self.rows):
            rm = row_totals[ri]
            for ci, cell in iter_items(row):
                cm = col_totals[ci]
                yield rm, cm, cell

    def iter_cells(self):
        for row in self.iter_rows():
            for cell in row:
                yield cell

    def iter_cols(self):
        for col in iter_vals(self.cols):
            yield iter_vals(col)

    def iter_rows(self):
        for row in iter_vals(self.rows):
            yield iter_vals(row)

    def iter_col_totals(self):
        return iter_vals(self.col_totals)

    def iter_row_totals(self):
        return iter_vals(self.row_totals)
