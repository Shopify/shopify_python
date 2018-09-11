import contextlib
import sys

import astroid
import pylint.testutils
import pytest

from shopify_python import google_styleguide


class TestGoogleStyleGuideChecker(pylint.testutils.CheckerTestCase):  # pylint: disable=too-many-public-methods

    CHECKER_CLASS = google_styleguide.GoogleStyleGuideChecker

    @contextlib.contextmanager
    def assert_adds_code_messages(self, codes, *messages):
        """Asserts that the checker received the list of messages, including only messages with the given codes."""
        yield
        got = [message for message in self.linter.release_messages() if message[0] in codes]
        msg = ('Expected messages did not match actual.\n'
               'Expected:\n%s\nGot:\n%s' % ('\n'.join(repr(m) for m in messages),
                                            '\n'.join(repr(m) for m in got)))
        assert list(messages) == got, msg

    def test_importing_function_fails(self):
        root = astroid.builder.parse("""
        from os.path import join
        from io import FileIO
        from os import environ
        from nonexistent_package import nonexistent_module
        def fnc():
            from other_nonexistent_package import nonexistent_module
        """)
        import_nodes = list(root.nodes_of_class(astroid.ImportFrom))
        tried_to_import = [
            'os.path.join',
            'io.FileIO',
            'os.environ',
            'nonexistent_package.nonexistent_module',
            'other_nonexistent_package.nonexistent_module',
        ]
        with self.assertAddsMessages(*[
                pylint.testutils.Message('import-modules-only', node=node, args={'child': child})
                for node, child in zip(import_nodes, tried_to_import)
        ]):
            self.walk(root)

    def test_importing_modules_passes(self):
        root = astroid.builder.parse("""
        from __future__ import unicode_literals  # Test default option to ignore __future__
        from xml import dom
        from xml import sax
        def fnc():
            from xml import dom
        """)
        with self.assertNoMessages():
            self.walk(root)

    def test_importing_relatively_fails(self):
        root = astroid.builder.parse("""
        from . import string
        from .. import string, os
        """)
        with self.assert_adds_code_messages(
                ['import-full-path'],
                pylint.testutils.Message('import-full-path', node=root.body[0], args={'module': '.string'}),
                pylint.testutils.Message('import-full-path', node=root.body[1], args={'module': '.string'}),
                pylint.testutils.Message('import-full-path', node=root.body[1], args={'module': '.os'}),
        ):
            self.walk(root)

    def test_global_variables(self):
        root = astroid.builder.parse("""
        module_var, other_module_var = 10
        another_module_var = 1
        __version__ = '0.0.0'
        CONSTANT = 10
        _OTHER_CONSTANT = sum(x)
        Point = namedtuple('Point', ['x', 'y'])
        _Point = namedtuple('_Point', ['x', 'y'])
        class MyClass(object):
            class_var = 10
        """)
        with self.assertAddsMessages(
                pylint.testutils.Message(
                    'global-variable', node=root.body[0].targets[0].elts[0], args={'name': 'module_var'}),
                pylint.testutils.Message(
                    'global-variable', node=root.body[0].targets[0].elts[1], args={'name': 'other_module_var'}),
                pylint.testutils.Message(
                    'global-variable', node=root.body[1].targets[0], args={'name': 'another_module_var'}),
        ):
            self.walk(root)

    @pytest.mark.skipif(sys.version_info >= (3, 0), reason="Tests code that is Python 3 incompatible")
    def test_using_archaic_raise_fails(self):
        root = astroid.builder.parse("""
        raise MyException, 'Error message'
        """)
        node = root.body[0]
        message = pylint.testutils.Message('two-arg-exception', node=node)
        with self.assertAddsMessages(message):
            self.walk(root)

        root = astroid.builder.parse("""
        raise 'Error message'
        """)
        node = root.body[0]
        message = pylint.testutils.Message('string-exception', node=node)
        with self.assertAddsMessages(message):
            self.walk(root)

    @pytest.mark.skipif(sys.version_info < (3, 0), reason="Tests code that is Python 2 incompatible")
    def test_using_reraise_passes(self):
        root = astroid.builder.parse("""
        try:
            x = 1
        except Exception as exc:
            raise MyException from exc
        """)
        with self.assertNoMessages():
            self.walk(root)

    def test_catch_standard_error_fails(self):
        root = astroid.builder.parse("""
        try:
            pass
        except StandardError:
            pass
        """)
        node = root.body[0].handlers[0]
        message = pylint.testutils.Message('catch-standard-error', node=node)
        with self.assertAddsMessages(message):
            self.walk(root)

    def test_catch_blank_passes(self):
        root = astroid.builder.parse("""
        try:
            pass
        except:
            pass
        """)
        with self.assertAddsMessages():
            self.walk(root)

    def test_try_exc_fnly_complexity(self):
        root = astroid.builder.parse("""
        try:
            a = [x for x in range(0, 10) if x < 5]
            a = sum((x * 2 for x in a)) + (a ** 2)
        except AssertionError as assert_error:
            if set(assert_error).startswith('Division by zero'):
                raise MyException(assert_error, [x for x in range(0, 10) if x < 5])
            else:
                a = [x for x in range(0, 10) if x < 5]
                raise
        finally:
            a = [x for x in range(0, 10) if x < 5]
            a = sum((x * 2 for x in a))
        """)
        try_finally = root.body[0]
        try_except = try_finally.body[0]
        with self.assertAddsMessages(
                pylint.testutils.Message('finally-too-long', node=try_finally, args={'found': 24}),
                pylint.testutils.Message('try-too-long', node=try_except, args={'found': 28}),
                pylint.testutils.Message('except-too-long', node=try_except.handlers[0], args={'found': 39}),
        ):
            self.walk(root)

    def test_multiple_from_imports(self):
        root = astroid.builder.parse("""
        import sys
        from package.module import module1, module2
        from other_package import other_module as F
        """)

        module2_node = root['module2']
        message = pylint.testutils.Message(
            'multiple-import-items',
            node=module2_node,
            args={
                'module': 'package.module'})
        with self.assert_adds_code_messages(['multiple-import-items'], message):
            self.walk(root)

    def test_use_simple_lambdas(self):
        root = astroid.builder.parse("""
        def fnc():
            good = lambda x, y: x if x % 2 == 0 else y
            bad = lambda x, y: (x * 2 * 3 + 4) if x % 2 == 0 else (y * 2 * 3 + 4)
        """)
        fnc = root.body[0]
        bad_list_comp = fnc.body[1].value
        message = pylint.testutils.Message('use-simple-lambdas', node=bad_list_comp, args={'found': 24})
        with self.assertAddsMessages(message):
            self.walk(root)

    def test_use_simple_list_comps(self):
        root = astroid.builder.parse("""
        def fnc():
            good = [x for x in range(0,10)]
            bad = [(x, y) for x in range(0,10) for y in range(0,10)]
        """)
        fnc = root.body[0]
        bad_list_comp = fnc.body[1].value
        message = pylint.testutils.Message('complex-list-comp', node=bad_list_comp)
        with self.assertAddsMessages(message):
            self.walk(root)

    def test_use_cond_exprs(self):
        # this parsed expression should send a message
        root_to_msg = astroid.builder.parse("""
            if 1 < 2:
                num = 1
            else:
                num = 2
            """)

        # this parsed expression should NOT send a message
        root_not_msg = astroid.builder.parse("""
            if 1 < 2:
                num = 1
            else:
                dum = 2
            """)

        # root_to_msg should add a message
        if_node = root_to_msg.body[0]
        message = pylint.testutils.Message('cond-expr', node=if_node)
        with self.assertAddsMessages(message):
            self.walk(root_to_msg)

        # root_not_msg should add no messages
        with self.assertNoMessages():
            self.walk(root_not_msg)

    def test_unary_lambda_func_with_complex_operand_allowed(self):
        unary_root = astroid.builder.parse("""
        def unaryfnc():
            unary_pass = map(lambda x: not (x+3), [1, 2, 3, 4])
        """)
        with self.assertNoMessages():
            self.walk(unary_root)

    def test_unary_lambda_func_without_operand_name_allowed(self):
        unary_root = astroid.builder.parse("""
        def unaryfnc():
            unary_pass = map(lambda x: not x.attribute, [1, 2, 3, 4])
        """)
        with self.assertNoMessages():
            self.walk(unary_root)

    def test_unary_lambda_func_with_unknown_operator_allowed(self, monkeypatch):
        monkeypatch.setattr(google_styleguide.GoogleStyleGuideChecker, 'UNARY_OPERATORS', dict())
        unary_root = astroid.builder.parse("""
        def unaryfnc():
            unary_pass = map(lambda x: not x, [1, 2, 3, 4])
        """)
        with self.assertNoMessages():
            self.walk(unary_root)

    @pytest.mark.parametrize('operator', [
        '+', '<'
    ])
    def test_binary_lambda_func_with_unknown_operator_allowed(self, operator, monkeypatch):
        monkeypatch.setattr(google_styleguide.GoogleStyleGuideChecker, 'BINARY_OPERATORS', dict())
        unary_root = astroid.builder.parse("""
        def unaryfnc():
            binary_pass = map(lambda x, y: x %s y, [(1, 2), (3, 4)])
        """ % operator)
        with self.assertNoMessages():
            self.walk(unary_root)

    @pytest.mark.parametrize('test_case', [
        ('- x', 'neg'),
        ('~ x', 'invert'),
        ('not x', 'not_'),
        ('+ x', 'pos')
    ])
    def test_unary_lambda_func(self, test_case):
        (expression, op_name) = test_case
        unary_root = astroid.builder.parse("""
        def unaryfnc():
            unary_fail = map(lambda x: {}, [1, 2, 3, 4])
        """.format(expression))

        ulam_fail = unary_root.body[0].body[0].value.args[0]
        unary_message = pylint.testutils.Message('lambda-func', node=ulam_fail, args={
            'op': 'operator.{}'.format(op_name),
            'lambda_fun': 'lambda x: {}'.format(expression)
        })
        with self.assertAddsMessages(unary_message):
            self.walk(unary_root)

    @pytest.mark.parametrize('test_case', [
        ('x + y', 'add'),
        ('x - y', 'sub'),
        ('x * y', 'mul'),
        ('x / y', 'truediv'),
        ('x ** y', 'pow'),
        ('x % y', 'modulo'),
        ('x < y', 'lt'),
        ('x <= y', 'le'),
        ('x == y', 'eq'),
        ('x != y', 'ne'),
        ('x >= y', 'ge'),
        ('x > y', 'gt'),
        ('x is y', 'is')
    ])
    def test_binary_lambda_func(self, test_case):
        (expression, op_name) = test_case
        binary_root = astroid.builder.parse("""
        def binaryfnc():
            binary_fail = reduce(lambda x, y: {}, [1, 2, 3, 4])
        """.format(expression))

        binary_fail = binary_root.body[0].body[0].value.args[0]
        binary_message = pylint.testutils.Message('lambda-func', node=binary_fail.body, args={
            'op': 'operator.{}'.format(op_name),
            'lambda_fun': 'lambda x, y: {}'.format(expression)
        })
        with self.assertAddsMessages(binary_message):
            self.walk(binary_root)

    @pytest.mark.parametrize('expression', [
        'map(lambda x: x + 3, [1, 2, 3, 4])',
        'reduce(lambda x, y, z: x * y + z, [1, 2, 3])'
    ])
    def test_allowed_binary_operation(self, expression):
        binary_root = astroid.builder.parse("""
        def binaryfnc():
            binary_pass = {}
        """.format(expression))
        with self.assertNoMessages():
            self.walk(binary_root)

    def test_class_def_blank_line(self):
        root = astroid.builder.parse("""
            class SomePipeline(object):
                def apply(content):
                    return content.withColumn('zero', F.lit(0.0))

            class Fact(object):
                INPUTS = {}
                def apply(self):
                    pass

            class Stage(object):
                INPUTS = {}

                OUTPUTS = {}
                def apply(self):
                    pass
            """)
        with self.assertAddsMessages(
                *[pylint.testutils.Message('blank-line-after-class-required', node=root.body[0]),
                  pylint.testutils.Message('blank-line-after-class-required', node=root.body[1]),
                  pylint.testutils.Message('blank-line-after-class-required', node=root.body[2])]
        ):
            self.walk(root)

        with self.assertNoMessages():
            self.walk(astroid.builder.parse("""
            class SomePipeline(object):

                def apply(content):
                    return content.withColumn('zero', F.lit(0.0))

            class FirstStage(object):
                pass

            class SecondStage(object):
                INPUTS = {}
                OUTPUTS = {}

                def check():
                    pass

                def apply():
                    pass
            """))
