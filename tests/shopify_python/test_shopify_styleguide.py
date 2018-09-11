import mock
import pylint.testutils

from shopify_python import shopify_styleguide


class TestShopifyStyleGuideChecker(pylint.testutils.CheckerTestCase):

    CHECKER_CLASS = shopify_styleguide.ShopifyStyleGuideChecker

    def test_disable_name_only(self):

        # Patch 'msgs_store'
        mock_msgs_store = mock.Mock()
        mock_msgs_store.get_msg_display_string = mock.Mock()
        mock_msgs_store.get_msg_display_string.return_value = 'mocked'
        setattr(self.linter, 'msgs_store', mock_msgs_store)

        # Create tokens
        tokens = pylint.testutils._tokenize_str(  # pylint: disable=protected-access
            """
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

        # Expected
        expected_line_msgcodes = [
            (2, 'W0611'),
            (3, 'W0611'),
            (3, 'C0302'),
            (3, 'C0303'),
            (4, 'W0611'),
            (5, 'W0611'),
            (6, 'W0611'),
            (8, 'C0112'),
        ]

        # Test
        with self.assertAddsMessages(*[
                pylint.testutils.Message('disable-name-only', line=line, args={'code': code, 'name': 'mocked'})
                for line, code in expected_line_msgcodes
        ]):
            self.checker.process_tokens(tokens)
        mock_msgs_store.get_msg_display_string.assert_has_calls(
            [mock.call(code) for _, code in expected_line_msgcodes])
