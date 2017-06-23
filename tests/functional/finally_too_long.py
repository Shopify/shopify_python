# pylint: disable=undefined-variable,invalid-name,missing-docstring

try:  # [finally-too-long]
    letsRunThisFunction()
except Error as error:
    pass
finally:
    x = "this time"
    y = "next time"
    for i in range(0, 50):
        x += y
    for i in range(0, 50):
        y += x
    GetToThisFunc(x, y)

try:
    runThisFcnAgain()
finally:
    runNextFcn()
