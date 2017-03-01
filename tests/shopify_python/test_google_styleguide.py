import astroid.test_utils
import pylint.testutils

from shopify_python import google_styleguide


class TestGoogleStyleGuideChecker(pylint.testutils.CheckerTestCase):

    CHECKER_CLASS = google_styleguide.GoogleStyleGuideChecker

    def test_importing_function_fails(self):
        root = astroid.builder.parse("""
        from os.path import join
        """)
        node = root.__dict__['body'][0]
        message = pylint.testutils.Message('import-modules-only',
                                           node=node)
        with self.assertAddsMessages(message):
            self.walk(root)

    def test_importing_modules_passes(self):
        root = astroid.builder.parse("""
        from __future__ import unicode_literals
        import sys
        from xml import dom
        from xml import sax
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
