# pylint: disable=invalid-name,used-before-assignment,missing-docstring

if xeo > 3:  # cond-expr
    xeo = 2
else:
    xeo = -2

if xeo > 3:  # should be fine
    xeo = 3
else:
    beo = 2
