import collections
from copy import deepcopy


def deepupdate(d, u):
    """Recursively update one dict with contents of another"""
    for k, v in u.iteritems():
        d[k] = deepupdate(d.get(k, {}), v) \
            if isinstance(v, collections.Mapping) \
            else v
    return d


def override(parent, child):
    """Inherit child from parent and return a new object"""
    return deepupdate(deepcopy(parent), child)
