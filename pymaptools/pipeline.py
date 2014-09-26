"""
``Pipe`` is a basic pipeline for processing data in sequence. You can create
pipes by composing ``Step`` instances (or any callables).
"""

import abc
import contextlib
import itertools as it
from functools import partial


class Step(object):
    """
    base class for steps (for use with Pipe)
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __call__(self, obj):
        """Process one piece of content"""

    def __enter__(self):
        """Enter context"""
        return self

    def __exit__(self, type, value, traceback):
        """Exit context (tear down)"""
        self.on_exit()

    def on_exit(self):
        """callback when pipeline is done or error occured"""
        pass


class StepWrapper(Step):
    """
    A wrapper for plain callables and other step-like objects not derived
    from Step
    """
    def __init__(self, fun):
        self._callable = fun

    def __call__(self, obj):
        return self._callable(obj)


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
        steps_with_exit = []
        for step in steps:
            assert hasattr(step, '__call__')
            if not isinstance(step, Step):
                step = StepWrapper(step)
            steps_with_exit.append(step)
        self.steps = steps_with_exit

    @staticmethod
    def apply_step(step, obj):
        """
        apply step and return an empty list if result is not iterable
        """
        result = step(obj)
        return result if hasattr(result, '__iter__') else []

    def apply_steps(self, obj):
        """
        run all the steps on a single object
        """
        results = [obj]
        for step in self.steps:
            apply_step = partial(self.apply_step, step)
            # note: some exceptions may not be caught if imap is used
            # instead of map here below:
            results = list(it.chain(*map(apply_step, results)))
        for result in results:
            yield result

    def run(self, input_iter):
        """
        run all the steps on input iterator
        """
        with contextlib.nested(*self.steps) as entered_steps:
            for i, step in enumerate(entered_steps):
                self.steps[i] = step
            for obj in input_iter:
                for _ in self.apply_steps(obj):
                    pass
