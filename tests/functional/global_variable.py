# pylint: disable=invalid-name,too-few-public-methods,missing-docstring,unpacking-non-sequence,undefined-variable
# pylint: disable=old-style-class

my_int = 77  # [global-variable]


class Integers:

    def __init__(self):
        pass

    one = 1
    two = 2
    three = 3
    four = 4
    five = 5


module_var, other_module_var = 10  # [global-variable, global-variable]

another_module_var = 1  # [global-variable]

__version__ = '0.0.0'

CONSTANT = 10

_OTHER_CONSTANT = sum(x)

Point = namedtuple('Point', ['x', 'y'])

_Point = namedtuple('_Point', ['x', 'y'])


class MyClass:

    def __init__(self):
        pass

    class_var = 10
