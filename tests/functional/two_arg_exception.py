# pylint: disable=unreachable,undefined-variable,missing-docstring,deprecated-exception

raise 'This is the error message'
raise Exception('this is the error message')
raise Exception
raise MyException, 'message'  # [two-arg-exception]
