import re
import tokenize
import typing  # pylint: disable=unused-import

import pylint.utils

from pylint import checkers
from pylint import interfaces
from pylint import lint  # pylint: disable=unused-import


def register_checkers(linter):  # type: (lint.PyLinter) -> None
    """Register checkers."""
    linter.register_checker(ShopifyStyleGuideChecker(linter))


class ShopifyStyleGuideChecker(checkers.BaseTokenChecker):
    """
    Pylint checker for Shopify-specific Code Style.
    """
    __implements__ = (interfaces.ITokenChecker,)

    name = 'shopify-styleguide-checker'

    msgs = {
        'C6101': ("%(code)s disabled as a message code, use '%(name)s' instead",
                  'disable-name-only',
                  "Disable pylint rules via message name (e.g. unused-import) and not message code (e.g. W0611) to "
                  "help code reviewers understand why a linter rule was disabled for a line of code."),
    }

    RE_PYLINT_DISABLE = re.compile(r'^#[ \t]*pylint:[ \t]*(disable|enable)[ \t]*=(?P<messages>[a-zA-Z0-9\-_, \t]+)$')
    RE_PYLINT_MESSAGE_CODE = re.compile(r'^[A-Z]{1,2}[0-9]{4}$')

    def process_tokens(self, tokens):
        # type: (typing.Sequence[typing.Tuple]) -> None
        for _type, string, start, _, _ in tokens:
            start_row, _ = start
            if _type == tokenize.COMMENT:

                def get_name(code):
                    try:
                        return self.linter.msgs_store.get_msg_display_string(code)
                    except pylint.utils.UnknownMessageError:
                        return 'unknown'

                matches = self.RE_PYLINT_DISABLE.match(string)
                if matches:
                    for msg in matches.group('messages').split(','):
                        msg = msg.strip()
                        if self.RE_PYLINT_MESSAGE_CODE.match(msg):
                            self.add_message('disable-name-only', line=start_row,
                                             args={'code': msg, 'name': get_name(msg)})
