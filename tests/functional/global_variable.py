# pylint: disable=invalid-name,too-few-public-methods,missing-docstring,unpacking-non-sequence,undefined-variable,useless-object-inheritance

my_int = 77  # [global-variable]


class Integers(object):
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


class MyClass(object):
    class_var = 10
