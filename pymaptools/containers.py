import copy
from itertools import izip
from functools import partial
from collections import OrderedDict, Callable, defaultdict
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
                          copy.deepcopy(self.items(), memo=memo))


OrderedCounter = partial(DefaultOrderedDict, int)


class TableOfCounts(object):

    """
    Example:

    >>> table2 = TableOfCounts(cols=[(0, 0), (45, 0)])
    >>> table2.grand_total
    45
    >>> table1 = TableOfCounts(rows=[(1, 5), (4, 6)])
    >>> table1.col_totals.values()
    [5, 11]
    """
    # TODO: use one of Scipy's sparse matrix representations instead of
    # a dict of dicts

    def __init__(self, rows=None, cols=None,
                 row_totals=None, col_totals=None, grand_total=None):
        self._rows = rows
        self._cols = cols
        self._row_totals = row_totals
        self._col_totals = col_totals
        self._grand_total = grand_total

    @property
    def rows(self):
        """Rows
        """
        _rows = self._rows
        if _rows is None:
            _rows = self._rows = DefaultOrderedDict(OrderedCounter)
            for cid, col in iter_items(self._cols):
                for rid, cell in iter_items(col):
                    _rows[rid][cid] = cell
        return _rows

    @property
    def cols(self):
        """Columns
        """
        _cols = self._cols
        if _cols is None:
            _cols = self._cols = DefaultOrderedDict(OrderedCounter)
            for rid, row in iter_items(self._rows):
                for cid, cell in iter_items(row):
                    _cols[cid][rid] = cell
        return _cols

    @property
    def row_totals(self):
        """Row Totals

        >>> t = TableOfCounts.from_cells([1, 2, 3, 4, 5, 6], num_cols=2)
        >>> t.row_totals.values()
        [3, 7, 11]

        Ensure attribute caching::

        >>> t._row_totals[1]
        7
        """
        _row_totals = self._row_totals
        if _row_totals is None:
            _row_totals = self._row_totals = OrderedCounter()
            for rid, row in iter_items(self.rows):
                _row_totals[rid] = sum(iter_vals(row))
        return _row_totals

    @property
    def col_totals(self):
        """Column Totals

        >>> t = TableOfCounts.from_cells([1, 2, 3, 4, 5, 6], num_cols=2)
        >>> t.col_totals.values()
        [9, 12]

        Ensure attribute caching::

        >>> t._col_totals[1]
        12
        """
        _col_totals = self._col_totals
        if _col_totals is None:
            _col_totals = self._col_totals = OrderedCounter()
            for rid, col in iter_items(self.cols):
                _col_totals[rid] = sum(iter_vals(col))
        return _col_totals

    @property
    def grand_total(self):
        _grand_total = self._grand_total
        if _grand_total is None:
            _grand_total = self._grand_total = sum(self.iter_row_totals())
        return _grand_total

    def to_labels(self):
        """Returns a tuple (ltrue, lpred). Inverse of ``from_labels``
        """
        ltrue = []
        lpred = []
        for ri, ci, count in self.iter_cells_with_indices():
            for _ in xrange(count):
                ltrue.append(ri)
                lpred.append(ci)
        return ltrue, lpred

    @classmethod
    def from_labels(cls, labels_true, labels_pred):
        rows = DefaultOrderedDict(OrderedCounter)
        for c, k in izip(labels_true, labels_pred):
            rows[c][k] += 1
        return cls(rows=rows)

    def __getitem__(self, key):
        return self.rows[key]

    @classmethod
    def from_cells(cls, iterable, num_cols):
        """Instantiate class from a reshaped iterable of cells

        >>> t = TableOfCounts.from_cells([1, 2, 3, 4, 5, 6], num_cols=2)
        >>> t[1][1]
        4
        """
        row_idx = 0
        rows = DefaultOrderedDict(OrderedCounter)
        for idx, cell in enumerate(iterable):
            col_idx = idx % num_cols
            rows[row_idx][col_idx] = cell
            if col_idx == num_cols - 1:
                row_idx += 1
        return cls(rows=rows)

    def to_partitions(self):
        """Inverse to ``from_partitions`` constructor

        >>> p1 = [[5, 6, 7, 8], [9, 10, 11], [0, 1, 2, 3, 4]]
        >>> p2 = [[0, 1, 5, 6, 9], [2, 3, 7], [8, 10, 11], [4]]
        >>> t = TableOfCounts.from_partitions(p1, p2)
        >>> t.to_partitions()
        ([[5, 6, 7, 8], [9, 10, 11], [0, 1, 2, 3, 4]], [[0, 1, 5, 6, 9], [2, 3, 7], [8, 10, 11], [4]])
        """
        point = 0
        ptrue = defaultdict(list)
        ppred = defaultdict(list)
        for ri, ci, count in self.iter_cells_with_indices():
            for _ in xrange(count):
                ptrue[ri].append(point)
                ppred[ci].append(point)
                point += 1
        return ptrue.values(), ppred.values()

    @classmethod
    def from_partitions(cls, partitions1, partitions2):
        """Construct a coincidence table from two import partitionings

        Partitions are non-overlapping clusters.

        >>> p1 = [[1, 2, 3, 4], [5, 6, 7], [8, 9, 10, 11, 12]]
        >>> p2 = [[2, 4, 6, 8, 10], [3, 9, 12], [1, 5, 7], [11]]
        >>> t = TableOfCounts.from_partitions(p1, p2)
        >>> t.to_labels()
        ([0, 0, 0, 0, 1, 1, 1, 2, 2, 2, 2, 2], [0, 0, 1, 2, 0, 2, 2, 0, 0, 1, 1, 3])

        """
        ltrue, lpred = partitions_to_labels(partitions1, partitions2)
        return cls.from_labels(ltrue, lpred)

    def to_clusters(self):
        """Return a coded representation of clusters

        In the representations, clusters are lists, classes are integers

        >>> p1 = [[1, 2, 3, 4], [5, 6, 7], [8, 9, 10, 11, 12]]
        >>> p2 = [[2, 4, 6, 8, 10], [3, 9, 12], [1, 5, 7], [11]]
        >>> t = TableOfCounts.from_partitions(p1, p2)
        >>> t.to_clusters()
        [[0, 0, 1, 2, 2], [0, 2, 2], [0, 1, 1], [2]]
        """
        ltrue, lpred = self.to_labels()
        return labels_to_clusters(ltrue, lpred)

    @classmethod
    def from_clusters(cls, clusters):
        """Construct an instance from to_clusters() output

        >>> clusters = [[2, 2, 0, 0, 1], [2, 2, 0], [0, 1, 1], [2]]
        >>> t = TableOfCounts.from_clusters(clusters)
        >>> t.to_clusters()
        [[2, 2, 0, 0, 1], [2, 2, 0], [0, 1, 1], [2]]
        """
        ltrue = []
        lpred = []
        for k, class_labels in iter_items(clusters):
            for c in class_labels:
                ltrue.append(c)
                lpred.append(k)
        return cls.from_labels(ltrue, lpred)

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


def partitions_to_labels(p1, p2):

    """Convert partitions to two arrays of labels

    Partitions are non-overlapping clusters

    >>> p1 = [[1, 2, 3, 4], [5, 6, 7], [8, 9, 10, 11, 12]]
    >>> p2 = [[2, 4, 6, 8, 10], [3, 9, 12], [1, 5, 7], [11]]
    >>> partitions_to_labels(p1, p2)
    ([0, 0, 1, 2, 2, 0, 2, 2, 0, 1, 1, 2], [0, 0, 0, 0, 0, 1, 1, 1, 2, 2, 2, 3])
    """

    ltrue = []
    lpred = []

    points_to_pids_1 = {}

    for pid1, points in iter_items(p1):
        for point in points:
            if point in points_to_pids_1:
                raise ValueError("Non-unique element found: not a partitioning")
            else:
                points_to_pids_1[point] = pid1

    seen_p2 = set()
    for pid2, points in iter_items(p2):
        for point in points:
            if point in seen_p2:
                raise ValueError("Non-unique element found: not a partitioning")
            try:
                pid1 = points_to_pids_1[point]
            except KeyError:
                raise ValueError("Second partitioning had an element not in first")
            else:
                del points_to_pids_1[point]
            ltrue.append(pid1)
            lpred.append(pid2)
            seen_p2.add(point)

    if points_to_pids_1:
        raise ValueError("Second partitioning did not cover all elements in first")

    return ltrue, lpred


def labels_to_clusters(labels_true, labels_pred):
    """Convert pair of label arrays to clusters of true labels

    Exact inverse of ``clusters_to_labels``

    >>> pair = ([1, 1, 1, 1, 1, 0, 0],
    ...         [0, 0, 0, 1, 1, 2, 3])
    >>> labels_to_clusters(*pair)
    [[1, 1, 1], [1, 1], [0], [0]]

    """
    result = defaultdict(list)
    for label_true, label_pred in izip(labels_true, labels_pred):
        result[label_pred].append(label_true)
    return result.values()


def clusters_to_labels(iterable):
    """Convert clusters of true labels to pair of label arrays

    Exact inverse of ``labels_to_clusters``

    >>> clusters = [[1, 1, 1], [1, 1], [0], [0]]
    >>> clusters_to_labels(clusters)
    ([1, 1, 1, 1, 1, 0, 0], [0, 0, 0, 1, 1, 2, 3])

    """
    labels_true = []
    labels_pred = []
    for cluster_idx, cluster in enumerate(iterable):
        for label_true in cluster:
            labels_true.append(label_true)
            labels_pred.append(cluster_idx)
    return labels_true, labels_pred
