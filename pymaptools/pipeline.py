import abc
from functools import partial
import itertools as it


class Step(object):
    """
    base class for steps (for use with Pipe)
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __call__(self, obj):
        """Process one piece of content"""


class Pipe(object):

    """
    Apply a series of steps to an iterator

    >>> def deserialize(obj):
    ...     yield int(obj)
    ...
    >>> def square(obj):
    ...     yield obj * obj
    ...
    >>> class Sum(Step):
    ...     def __init__(self):
    ...         self.sum = 0
    ...     def __call__(self, obj):
    ...         self.sum += obj
    ...
    >>> sumsq = Pipe([deserialize, square, Sum()])
    >>> sumsq.run(["1", "2", "3"])
    >>> sumsq.steps[-1].sum
    14

    """

    def __init__(self, steps):
        """
        given an array of step objects, compose them into a pipe
        """
        self.steps = steps

    def apply_step(self, step, obj):
        """
        apply step and return an empty list if result is not iterable
        """
        result = step(obj)
        return result if hasattr(result, '__iter__') else []

    def apply_steps(self, obj):
        """
        run all the steps on a single object
        """
        new_vals = [obj]
        for step in self.steps:
            apply_step = partial(self.apply_step, step)
            new_vals = list(it.chain(*it.imap(apply_step, new_vals)))
        for result in new_vals:
            yield result

    def run(self, input_iter):
        """
        run all the steps on input iterator
        """
        for obj in input_iter:
            for _ in self.apply_steps(obj):
                pass
