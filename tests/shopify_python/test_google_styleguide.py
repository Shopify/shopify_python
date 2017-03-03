import sys

import astroid.test_utils
import pylint.testutils
import pytest

from shopify_python import google_styleguide


class TestGoogleStyleGuideChecker(pylint.testutils.CheckerTestCase):

    CHECKER_CLASS = google_styleguide.GoogleStyleGuideChecker

    def test_importing_function_fails(self):
        root = astroid.builder.parse("""
        from os.path import join
        """)
        node = root.__dict__['body'][0]
        message = pylint.testutils.Message('import-modules-only', node=node)
        with self.assertAddsMessages(message):
            self.walk(root)

    def test_importing_modules_passes(self):
        root = astroid.builder.parse("""
        from __future__ import unicode_literals
        from xml import dom
        from xml import sax
        from nonexistent_package import nonexistent_module
        """)
        with self.assertNoMessages():
            self.walk(root)

    def test_importing_relatively_fails(self):
        root = astroid.builder.parse("""
        from . import string
        from .. import string
        """)
        messages = []
        for node in root.__dict__['body']:
            messages.append(pylint.testutils.Message('import-full-path', node=node))
        with self.assertAddsMessages(*messages):
            self.walk(root)

    def test_global_variables_fail(self):
        root = astroid.builder.parse("""
        module_var, other_module_var = 10
        __version__ = '0.0.0'
        class MyClass(object):
            class_var = 10
        """)
        with self.assertAddsMessages(
            pylint.testutils.Message('global-variable', node=root.body[0].targets[0].elts[0]),
            pylint.testutils.Message('global-variable', node=root.body[0].targets[0].elts[1]),
        ):
            self.walk(root)

    @pytest.mark.skipif(sys.version_info >= (3, 0), reason="Tests code that is Python 3 incompatible")
    def test_using_archaic_raise_fails(self):
        root = astroid.builder.parse("""
        raise MyException, 'Error message'
        raise 'Error message'
        """)
        node = root.__dict__['body'][0]
        message = pylint.testutils.Message('two-arg-exception', node=node)
        with self.assertAddsMessages(message):
            self.walk(root)

    def test_catch_standard_error_fails(self):
        root = astroid.builder.parse("""
        try:
            pass
        except StandardError:
            pass
        """)
        node = root.__dict__['body'][0].__dict__['handlers'][0]
        message = pylint.testutils.Message('catch-standard-error', node=node)
        with self.assertAddsMessages(message):
            self.walk(root)

    def test_try_exc_finally_size(self):
        root = astroid.builder.parse("""
        try:
            # Comments are OK.
            # They are needed to document
            # complicated exception
            # scenarious and should
            # not be penalized.
            l = 1
        except AssertionError:
            # Comments are OK.
            # They are needed to document
            # complicated exception
            # scenarious and should
            # not be penalized.
            raise
        finally:
            # Comments are OK.
            # They are needed to document
            # complicated exception
            # scenarious and should
            # not be penalized.
            l = 1

        try:
            l = 1
            l = 2
            l = 3
            l = 4
            l = 5
            l = 6
        except AssertionError:
            l = 1
            l = 2
            l = 3
            l = 4
            l = 5
            l = 6
        finally:
            l = 1
            l = 2
            l = 3
            l = 4
            l = 5
            l = 6
        """)
        with self.assertAddsMessages(
            pylint.testutils.Message('finally-too-long', node=root.body[1]),
            pylint.testutils.Message('try-too-long', node=root.body[1].body[0]),
            pylint.testutils.Message('except-too-long', node=root.body[1].body[0].handlers[0]),
        ):
            self.walk(root)
