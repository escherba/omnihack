from itertools import izip
from functools import partial
from collections import defaultdict, Counter, Mapping
from pymaptools.iter import iter_items, iter_keys, iter_vals
from pymaptools._cyordereddict import OrderedDict
from pymaptools._containers import OrderedSet, DefaultOrderedDict


OrderedCounter = partial(DefaultOrderedDict, int)


class Struct(object):
    """An abstract class with namespace-like properties

    Note:

    collections.namedtuple is similar in concept but is too strict
    (requires all the keys every time you instantiate)

    bunch.Bunch object is very close to what we want, but it is not
    strict (it will not throw an error if we try to assign to it a
    a property it does not know about)::

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


class CrossTab(object):

    """Represents a RxC contigency table (cross-tabulation)

    A contingency table represents a cross-tabulation of either categorical
    (nominal) or ordinal variables [1]_. A related concept is a 2D histogram
    except a histogram represents bins drawn from a continuous distribution,
    while a contingency table can also represent discrete distributions.
    Another related concept is correlation matrix, which is a special case of a
    contingency table where rows and columns have the same cardinality and
    represent two different mesurements of the same vector of variables.

    You can construct a dense ``CrossTab`` instance given either rows or
    columns (in a 2D-array format)::

        >>> t1 = OrderedCrossTab(rows=[(1, 5), (4, 6)])
        >>> t1.to_rows()
        [[1, 5], [4, 6]]
        >>> t2 = OrderedCrossTab(cols=[(0, 0), (45, 0)])
        >>> t2.to_rows()
        [[0, 45], [0, 0]]

    Given mapping containers, the contstructed instances of ``CrossTab``
    class will be sparse::

        >>> t3 = CrossTab(rows={"a": {"x": 2, "y": 3}, "b": {"x": 4, "y": 5}})
        >>> t3.grand_total
        14

    Note that the order of rows and columns in the "dict of dicts" case is not
    guaranteed. To guarantee row and column order, use ``OrderedCrossTab``
    subclass.

    See Also
    --------
    OrderedCrossTab, OrderedRowCrossTab, OrderedColCrossTab

    References
    ----------
    .. [1] `Wikipedia entry for Contingency Table
           <https://en.wikipedia.org/wiki/Contingency_table>`_
    """
    # TODO: use one of Scipy's sparse matrix representations instead of
    # a dict of dicts

    _col_type_1d = Counter
    _row_type_1d = Counter
    _col_type_2d = partial(defaultdict, _row_type_1d)
    _row_type_2d = partial(defaultdict, _col_type_1d)

    def __init__(self, rows=None, cols=None):
        self._rows = rows
        self._cols = cols
        self._row_totals = None
        self._col_totals = None
        self._grand_total = None

    @property
    def rows(self):
        """Table rows
        """
        _rows = self._rows
        if _rows is None:
            self._rows = _rows = self._row_type_2d()
            for cid, col in iter_items(self._cols):
                for rid, cell in iter_items(col):
                    _rows[rid][cid] = cell
        return _rows

    @property
    def cols(self):
        """Table columns
        """
        _cols = self._cols
        if _cols is None:
            self._cols = _cols = self._col_type_2d()
            for rid, row in iter_items(self._rows):
                for cid, cell in iter_items(row):
                    _cols[cid][rid] = cell
        return _cols

    @property
    def row_totals(self):
        """Row totals (right margin)

        ::

            >>> t = OrderedCrossTab.from_cells([1, 2, 3, 4, 5, 6], num_cols=2)
            >>> t.row_totals.values()
            [3, 7, 11]

        Ensure attribute caching::

            >>> t._row_totals[1]
            7
        """
        _row_totals = self._row_totals
        if _row_totals is None:
            self._row_totals = _row_totals = self._col_type_1d()
            for rid, row in iter_items(self.rows):
                _row_totals[rid] = sum(iter_vals(row))
        return _row_totals

    @property
    def col_totals(self):
        """Column totals (bottom margin)

        ::

            >>> t = OrderedCrossTab.from_cells([1, 2, 3, 4, 5, 6], num_cols=2)
            >>> t.col_totals.values()
            [9, 12]

        Ensure attribute caching::

            >>> t._col_totals[1]
            12
        """
        _col_totals = self._col_totals
        if _col_totals is None:
            self._col_totals = _col_totals = self._row_type_1d()
            for rid, col in iter_items(self.cols):
                _col_totals[rid] = sum(iter_vals(col))
        return _col_totals

    @property
    def grand_total(self):
        """Grand total of all counts
        """
        _grand_total = self._grand_total
        if _grand_total is None:
            self._grand_total = _grand_total = sum(self.iter_row_totals())
        return _grand_total

    def to_rows(self):
        """

        Example with dense matrices::

            >>> CrossTab(rows=[(1, 5), (4, 6)]).to_rows()
            [[1, 5], [4, 6]]
            >>> CrossTab(cols=[(0, 0), (45, 0)]).to_rows()
            [[0, 45], [0, 0]]

        Example with a sparse matrix::

            >>> a = [0, 2, 1, 1, 0, 3, 1, 3, 0, 1]
            >>> b = [0, 1, 1, 1, 0, 2, 1, 2, 3, 1]
            >>> t = OrderedCrossTab.from_labels(a, b)
            >>> t.to_rows()
            [[2, 1, 0, 0], [0, 0, 1, 0], [0, 0, 4, 0], [0, 0, 0, 2]]

        """
        row_form = []
        all_cols = list(iter_keys(self.col_totals))
        for row in iter_vals(self.rows):
            if isinstance(row, Mapping):
                row_vals = []
                for col in all_cols:
                    if col in row:
                        row_vals.append(row[col])
                    else:
                        row_vals.append(0)
                row_form.append(row_vals)
            else:
                row_form.append(list(row))
        return row_form

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
        rows = cls._row_type_2d()
        for c, k in izip(labels_true, labels_pred):
            rows[c][k] += 1
        return cls(rows=rows)

    def __getitem__(self, key):
        return self.rows[key]

    @classmethod
    def from_cells(cls, iterable, num_cols):
        """Instantiate class from a reshaped iterable of cells

        ::

            >>> t = CrossTab.from_cells([1, 2, 3, 4, 5, 6], num_cols=2)
            >>> t[1][1]
            4
        """
        row_idx = 0
        rows = cls._row_type_2d()
        for idx, cell in enumerate(iterable):
            col_idx = idx % num_cols
            rows[row_idx][col_idx] = cell
            if col_idx == num_cols - 1:
                row_idx += 1
        return cls(rows=rows)

    def to_partitions(self):
        """Inverse to ``from_partitions`` constructor

        ::

            >>> p1 = [[5, 6, 7, 8], [9, 10, 11], [0, 1, 2, 3, 4]]
            >>> p2 = [[0, 1, 5, 6, 9], [2, 3, 7], [8, 10, 11], [4]]
            >>> t = OrderedCrossTab.from_partitions(p1, p2)
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

        ::

            >>> p1 = [[1, 2, 3, 4], [5, 6, 7], [8, 9, 10, 11, 12]]
            >>> p2 = [[2, 4, 6, 8, 10], [3, 9, 12], [1, 5, 7], [11]]
            >>> t = OrderedCrossTab.from_partitions(p1, p2)
            >>> t.to_labels()
            ([0, 0, 0, 0, 1, 1, 1, 2, 2, 2, 2, 2], [0, 0, 1, 2, 0, 2, 2, 0, 0, 1, 1, 3])

        """
        ltrue, lpred = partitions_to_labels(partitions1, partitions2)
        return cls.from_labels(ltrue, lpred)

    def to_clusters(self):
        """Return a coded representation of clusters

        In the representations, clusters are lists, classes are integers

        ::

            >>> p1 = [[1, 2, 3, 4], [5, 6, 7], [8, 9, 10, 11, 12]]
            >>> p2 = [[2, 4, 6, 8, 10], [3, 9, 12], [1, 5, 7], [11]]
            >>> t = OrderedCrossTab.from_partitions(p1, p2)
            >>> t.to_clusters()
            [[0, 0, 1, 2, 2], [0, 2, 2], [0, 1, 1], [2]]
        """
        ltrue, lpred = self.to_labels()
        return labels_to_clusters(ltrue, lpred)

    @classmethod
    def from_clusters(cls, clusters):
        """Construct an instance from to_clusters() output

        ::

            >>> clusters = [[2, 2, 0, 0, 1], [2, 2, 0], [0, 1, 1], [2]]
            >>> t = OrderedCrossTab.from_clusters(clusters)
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


class OrderedRowCrossTab(CrossTab):

    """Specialization of ``CrossTab`` for ordinal row variable

    See Also
    --------
    CrossTab
    """
    _col_type_1d = Counter
    _row_type_1d = OrderedCounter
    _col_type_2d = partial(defaultdict, _row_type_1d)
    _row_type_2d = partial(DefaultOrderedDict, _col_type_1d)


class OrderedColCrossTab(CrossTab):

    """Specialization of ``CrossTab`` for ordinal column variable

    See Also
    --------
    CrossTab
    """
    _col_type_1d = OrderedCounter
    _row_type_1d = Counter
    _col_type_2d = partial(DefaultOrderedDict, _row_type_1d)
    _row_type_2d = partial(defaultdict, _col_type_1d)


class OrderedCrossTab(CrossTab):

    """Specialization of ``CrossTab`` for ordinal variables

    See Also
    --------
    CrossTab
    """
    _col_type_1d = OrderedCounter
    _row_type_1d = OrderedCounter
    _col_type_2d = partial(DefaultOrderedDict, _row_type_1d)
    _row_type_2d = partial(DefaultOrderedDict, _col_type_1d)


def partitions_to_labels(p1, p2):

    """Convert partitions to two arrays of labels

    Partitions are non-overlapping clusters::

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

    Exact inverse of ``clusters_to_labels``::

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

    Exact inverse of ``labels_to_clusters``::

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
