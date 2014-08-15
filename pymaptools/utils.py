import collections
from copy import deepcopy
from pkg_resources import resource_filename


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


def read_text_file(rel, filename):
    """Read text file ignoring comments beginning with pound sign"""
    with open(resource_filename(rel, filename), 'r') as fh:
        for line in fh:
            li = line.strip()
            if not li.startswith('#'):
                yield li
