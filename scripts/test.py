import json
import sys
from pymaptools.pipeline import Filter, Pipe

def deserialize(obj):
    """ demonstrate use of plain functions as callables
        demonstrate multiple outputs
    """
    try:
        array = json.loads(obj)["x"]
        for num in array:
            yield int(num)
    except:
        print "failed to deserialize `{}`".format(obj)

def filter_even(obj):
    """ demonstrate that values can be dropped """
    if obj % 2 == 0:
        yield obj

class Add(Filter):
    """ demonstrate use of state """
    def __init__(self, value):
        self.value = value

    def __call__(self, obj):
        yield obj + self.value

class MultiplyBy(Filter):
    def __init__(self, value):
        self.value = value

    def __call__(self, obj):
        yield obj * self.value

class Output(Filter):
    """ demonstrate that we can use IO """
    def __init__(self, handle):
        self.handle = handle

    def __call__(self, obj):
        self.handle.write(str(obj) + "\n")


# finally,
input_seq = ['{"x":[0,-6,4]}', '{"x":[12]}', '{"x":[34]}', '{"x":[-9]}',
             "Ceci n'est pas une pipe", '{"x":[4]}']
pipe = Pipe([
    deserialize,
    filter_even,
    Add(10),
    MultiplyBy(2),
    Output(sys.stdout)
])
pipe.run(input_seq)
