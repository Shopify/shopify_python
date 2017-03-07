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
        from io import FileIO
        from os import environ
        """)
        messages = []
        for node in root.body:
            messages.append(pylint.testutils.Message('import-modules-only', node=node))
        with self.assertAddsMessages(*messages):
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
        for node in root.body:
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

    def test_global_var_namedtuple(self):
        root = astroid.builder.parse("""
        import collections
        Point = collections.namedtuple('Point', ['x', 'y'])
        TaskStateSerialization = typing.Dict[str, typing.Any]
        """)
        with self.assertNoMessages():
            self.walk(root)

    @pytest.mark.skipif(sys.version_info < (3, 0), reason="Tests code that is Python 2 incompatible")
    def test_global_var_typing_passes(self):
        root = astroid.builder.parse("""
        import typing
        TaskStateSerialization = typing.Dict[str, typing.Any]
        """)
        with self.assertNoMessages():
            self.walk(root)

    @pytest.mark.skipif(sys.version_info >= (3, 0), reason="Tests code that is Python 3 incompatible")
    def test_using_archaic_raise_fails(self):
        root = astroid.builder.parse("""
        raise MyException, 'Error message'
        raise 'Error message'
        """)
        node = root.body[0]
        message = pylint.testutils.Message('two-arg-exception', node=node)
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
