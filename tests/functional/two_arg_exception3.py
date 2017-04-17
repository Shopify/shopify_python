# pylint: disable=unreachable,undefined-variable,missing-docstring

raise Exception('this is the error message')
raise Exception
raise MyException, 'message'  # [syntax-error]
