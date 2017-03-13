import pylint.testutils

from shopify_python import shopify_styleguide


class TestShopifyStyleGuideChecker(pylint.testutils.CheckerTestCase):

    CHECKER_CLASS = shopify_styleguide.ShopifyStyleGuideChecker

    def test_disable_name_only(self):
        tokens = pylint.testutils.tokenize_str("""
        import os  # pylint: disable=unused-import
        import os  # pylint: disable=unused-import,W0611
        import os  # pylint: disable=W0611,C0302,C0303
        import os  # pylint: disable=W0611
        import os  #pylint:disable=W0611
        import os  #  pylint:\t\t  disable  \t\t    = \t\t W0611
        def fnc():
            # pylint: disable=C0112
            pass
        """.strip())

        with self.assertAddsMessages(*[
            pylint.testutils.Message('disable-name-only', line=line, args={'code': code})
            for line, code in [(2, 'W0611'),
                               (3, 'W0611'),
                               (3, 'C0302'),
                               (3, 'C0303'),
                               (4, 'W0611'),
                               (5, 'W0611'),
                               (6, 'W0611'),
                               (8, 'C0112'), ]
        ]):
            self.checker.process_tokens(tokens)
