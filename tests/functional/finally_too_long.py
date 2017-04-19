# pylint: disable=bare-except,undefined-variable,invalid-name

try:  # [finally-too-long]
    letsRunThisFunction()
except:
    pass
finally:
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
