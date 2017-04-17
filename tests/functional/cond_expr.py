# This will add a message

def fnc(xeo):
    if xeo > 3: # [cond-expr]
        xeo = 2
    else:
        xeo = -2

# This won't add a message

def fnc2(xeo):
    if xeo > 3:
        xeo = 3
    else:
        beo = 2
    return xeo, beo
