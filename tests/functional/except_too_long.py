# pylint: disable=undefined-variable,invalid-name,missing-docstring

try:  # [except-too-long]
    letsRunThisFunction()
except Error as error:
    x = "this time"
    y = "next time"
    for i in range(0, 50):
        x += y
    for i in range(0, 50):
        y += x
    GetToThisFunc(x, y)

try:  # should be fine
    runThisFcnAgain()
finally:
    runNextFcn()
