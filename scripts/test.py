import json
import sys
from pymaptools.pipeline import Filter, Pipe

def deserialize(obj):
    """ demonstrate use of plain functions as callables """
    try:
        yield int(json.loads(obj)["x"])
    except:
        print "failed to deserialize `{}`".format(obj)

class FilterEven(Filter):
    def __call__(self, obj):
        """ demonstrate that values can be dropped """
        if obj % 2 == 0:
            yield obj

class Add(Filter):
    """ demonstrate use of state """
    def __init__(self, value):
        self.value = value

    def __call__(self, obj):
        yield obj + self.value

class Multiply(Filter):
    """ demonstrate use of state """
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
input_seq = ['{"x":0}', '{"x":12}', '{"x":34}', '{"x":-9}', "abracadabra", '{"x":1}', '{"x":4}']
pipe = Pipe([
    deserialize,
    FilterEven(),
    Add(10),
    Multiply(2),
    Output(sys.stdout)
])
pipe.run(input_seq)
