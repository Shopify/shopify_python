# pylint: disable=undefined-variable, missing-docstring


def fcn_to_fail():
    result = [(x, y) for x in range(10) for y in range(5) if x * y > 10]  # [complex-list-comp]
    return result


def one_to_pass():
    result = []
    for first in range(10):
        for second in range(5):
            result.append((first, second))
    return result


def two_to_pass():
    for first in xrange(5):
        for second in xrange(5):
            if first != second:
                for third in xrange(5):
                    if second != third:
                        yield (first, second, third)


def three_to_pass():
    return ((first, complicated_transform(first))
            for first in long_generator_function(parameter)
            if first is not None)


def four_to_pass():
    squares = [x * x for x in range(10)]
    return squares


def five_to_pass():
    eat(jelly_bean for jelly_bean in jelly_beans if jelly_bean.color == 'black')
