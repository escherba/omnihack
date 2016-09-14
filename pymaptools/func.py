import functools


def compose(*functions):
    """Function composition

    See https://mathieularose.com/function-composition-in-python/
    """
    return functools.reduce(lambda f, g: lambda x: f(g(x)), functions, lambda x: x)
