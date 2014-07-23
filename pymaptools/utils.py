import collections
from copy import deepcopy


def deepupdate(d, u):
    """
    Recursively update one dict with contents of another

    :param d: mapping being updated
    :type d: dict
    :param u: mapping to update with
    :type u: collections.Mapping
    :return: updated mapping
    :rtype: dict
    """
    for k, v in u.iteritems():
        d[k] = deepupdate(d.get(k, {}), v) \
            if isinstance(v, collections.Mapping) \
            else v
    return d


def override(parent, child):
    """Inherit child from parent and return a new object"""
    return deepupdate(deepcopy(parent), child)
