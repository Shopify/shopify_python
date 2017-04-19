# pylint: disable=invalid-name,undefined-variable,bare-except

try:  # should be fine
    pass
except:
    pass

try:  # [try-too-long]
    x = 50
    y = 70
    for i in range(0, 50):
        x = x*i
    for i in range(0, 50):
        y = y*x*i
    LogThisValue(y/x)
except:
    pass
