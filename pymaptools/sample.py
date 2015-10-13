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


def reservoir_iter(iterator, K, random_state=0):
    """Simple reservoir sampler
    """
    if K is None:
        return iterator
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


def reservoir_dict(iterator, field, Kdict, random_state=0):
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
