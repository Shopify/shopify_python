# pylint: disable=missing-docstring,pointless-statement

lambda x, y: x if x % 2 == 0 else y
lambda x, y: (x * 2 * 3 + 4) if x % 2 == 0 else (y * 2 * 3 + 4)  # [use-simple-lambdas]
