# pylint: disable=undefined-variable

def one():
    result = [(x, y) for x in range(10) for y in range(5) if x * y > 10]
    return result


def two():
    result = []
    for first in range(10):
        for second in range(5):
            result.append((first, second))
    return result

def three():
    for first in xrange(5):
        for second in xrange(5):
            if first != second:
                for third in xrange(5):
                    if second != third:
                        yield (first, second, third)

def four():
    return ((first, complicated_transform(first))
            for first in long_generator_function(parameter)
            if first is not None)

def will_pass2():
    squares = [x * x for x in range(10)]
    return squares

def will_pass3():
    eat(jelly_bean for jelly_bean in jelly_beans if jelly_bean.color == 'black')
