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
        module_var = 10
        class MyClass(object):
            class_var = 10
        """)
        node = root.__dict__['body'][0]
        message = pylint.testutils.Message('global-variable', node=node)
        with self.assertAddsMessages(message):
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
