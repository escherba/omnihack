import abc
from functools import partial
import itertools as it


class Filter(object):
    """
    base class for filters (for use with Pipe)
    """
    @abc.abstractmethod
    def __call__(self, obj):
        """Process one piece of content"""


class Pipe(object):

    """
    Apply a series of filters to an iterator
    """

    def __init__(self, filters):
        """
        given an array of filter objects, compose them into a pipe
        """
        self.filters = filters

    def apply_filter(self, filter, obj):
        """
        apply filter and return an empty list if result is not iterable
        """
        result = filter(obj)
        return result if hasattr(result, '__iter__') else []

    def apply_filters(self, obj):
        """
        run all the filters on a single object
        """
        gen_stack = [[obj]]
        for filt in self.filters:
            apply_filter = partial(self.apply_filter, filt)
            # note: a version w/o iterators (for debugging):
            #gen_stack.append(list(it.chain(*map(list, map(apply_filter, gen_stack[-1])))))
            gen_stack.append(it.chain(*it.imap(apply_filter, gen_stack[-1])))
        for result in gen_stack[-1]:
            yield result

    def run(self, input_iter):
        """
        run all the filters on input iterator
        """
        for obj in input_iter:
            for _ in self.apply_filters(obj):
                pass
