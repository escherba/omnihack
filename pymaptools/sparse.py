from collections import defaultdict
from funcy import partial
from scipy.sparse import coo_matrix


def dd2coo(dd):
    """
    Convert a dict of dicts to COO-type sparse matrix
    """
    # first create maps from key values to rows and columns

    # first level
    row_map = {k: idx for idx, k in enumerate(dd.iterkeys())}
    col_map = {k: idx for idx, k in enumerate(
        set(k for row in dd.itervalues() for k in row.iterkeys()))}

    values = []
    row_indices = []
    col_indices = []
    for row_key, row in dd.iteritems():
        for col_key, val in row.iteritems():
            values.append(val)
            row_indices.append(row_map[row_key])
            col_indices.append(col_map[col_key])

    return row_map, col_map, coo_matrix((values, (row_indices, col_indices)))


class CooBuilder(object):

    """A simple demonstration of dd2coo usage
    """
    def __init__(self, dtype):

        self._dict = defaultdict(partial(defaultdict, dtype))

    def add(self, x, y, val):

        self._dict[x][y] += val

    def assign(self, x, y, val):

        self._dict[x][y] = val

    def get_coo(self):

        return dd2coo(self._dict)
