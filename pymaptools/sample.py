import time
import os
import random
from itertools import chain
from collections import Counter, defaultdict


def random_seed():
    """Get a number that can be used to seed a random number generator
    """
    try:
        return int(os.urandom(7).encode('hex'), 16)
    except NotImplementedError:
        return hash(time.time())


def random_product(*args, **kwds):
    """Random selection from itertools.product(*args, **kwds)"""
    pools = map(tuple, args) * kwds.get('repeat', 1)
    return tuple(random.choice(pool) for pool in pools)


def random_permutation(iterable, r=None):
    """Random selection from itertools.permutations()
    """
    pool = tuple(iterable)
    r = len(pool) if r is None else r
    return tuple(random.sample(pool, r))


def random_combination(iterable, r):
    """Random selection from itertools.combinations()
    """
    pool = tuple(iterable)
    num = len(pool)
    indices = sorted(random.sample(xrange(num), r))
    return tuple(pool[i] for i in indices)


def random_combination_with_replacement(iterable, r):
    """Random selection from itertools.combinations_with_replacement()
    """
    pool = tuple(iterable)
    num = len(pool)
    indices = sorted(random.randrange(num) for i in xrange(r))
    return tuple(pool[i] for i in indices)


def reservoir_iter(iterator, K, random_state=None):
    """Simple reservoir sampler
    """
    if K is None:
        return iterator
    if random_state is not None:
        random.seed(random_state)
    sample = []
    for idx, item in enumerate(iterator):
        if len(sample) < K:
            sample.append(item)
        else:
            # accept with probability K / idx
            sample_idx = int(random.random() * idx)
            if sample_idx < K:
                sample[sample_idx] = item
    return iter(sample)


def reservoir_dict(iterator, field, Kdict, random_state=None):
    """Reservoir sampling over a list of dicts

    Given a field, and a mapping of field values to integers K,
    return a sample from the iterator such that for the field specified,
    each value occurs at most K times.  For example, for a binary ouput
    value Y, we would request

        field='Y', Kdict={0: 500, 1: 1000}

    to return 500 instances of Y=0 and 1000 instances of Y=1
    """
    if Kdict is None:
        return iterator
    if random_state is not None:
        random.seed(random_state)
    sample = defaultdict(list)
    field_indices = Counter()
    for row in iterator:
        field_val = row[field]
        if field_val in Kdict:
            idx = field_indices[field_val]
            field_list = sample[field_val]
            if len(field_list) < Kdict[field_val]:
                field_list.append(row)
            else:
                # accept with probability K / idx
                sample_idx = int(random.random() * idx)
                if sample_idx < Kdict[field_val]:
                    field_list[sample_idx] = row
            field_indices[field_val] += 1
    return list(chain.from_iterable(sample.itervalues()))


def discrete_sample(prob_dist, random_state=None):
    """Sample a random value from a discrete probability distribution
    represented as a dict: P(x=value) = prob_dist[value].

    Note: the prob_dist parameter doesn't have to be an ordered dict,
    however for performance reasons it is best if it is.

    :param prob_dist: the probability distribution
    :type prob_dist: collections.Mapping
    :returns: scalar drawn from the distribution
    :rtype: object
    """
    limit = 0.0
    if random_state is not None:
        random.seed(random_state)
    r = random.random()
    for key, val in prob_dist.iteritems():
        limit += val
        if r <= limit:
            return key