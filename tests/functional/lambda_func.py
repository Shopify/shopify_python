# pylint: disable=missing-docstring,deprecated-lambda
import operator as o
import functools as f

map(lambda x: - x, [1, 2, 3])  # [lambda-func]
map(o.neg, [1, 2, 3])


def foo1():
    return map(lambda x: + x, [1, 2, 3])  # [lambda-func]


def foo2():
    return map(o.abs, [1, 2, 3])


f.reduce(lambda x, y: x + y, [1, 2, 3, 4])  # [lambda-func]
f.reduce(o.add, [1, 2, 3, 4])


def foo3():
    return f.reduce(lambda x, y: x + y, [1, 2, 3, 4])  # [lambda-func]


def foo4():
    return f.reduce(o.add, [1, 2, 3, 4])
