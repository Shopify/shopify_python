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
        'C6102': ('Forbidden use of typing.Sequence[str], use typing.List[str] or some specific collection instead',
                  'sequence-of-string',
                  'Since str itself also satisfies typing.Sequence[str], the latter should be replaced by '
                  'a more specific iterable type, such as typing.List[str]')
    }

    RE_PYLINT_DISABLE = re.compile(r'^#[ \t]*pylint:[ \t]*(disable|enable)[ \t]*=(?P<messages>[a-zA-Z0-9\-_, \t]+)$')
    RE_PYLINT_MESSAGE_CODE = re.compile(r'^[A-Z]{1,2}[0-9]{4}$')

    RE_COMMENT_TYPE_ANNOTATION = re.compile(r'^# type.*:.*$')
    RE_SEQUENCE_STRING = re.compile(r'^.*Sequence\[str\].*$')

    def process_tokens(self, tokens):
        # type: (typing.Sequence[typing.Tuple]) -> None
        for _type, string, start, _, line in tokens:
            if _type == tokenize.NAME:
                self.__validate_name(string, start, line)
            elif _type == tokenize.COMMENT:
                self.__validate_comment(string, start)

    def __validate_comment(self, string, start):
        # type: (str, typing.Tuple[int, int]) -> None
        self.__disable_name_only(string, start)
        if self.RE_COMMENT_TYPE_ANNOTATION.match(string):
            self.__sequence_str(string, start)

    def __validate_name(self, string, start, line):
        # type: (str, typing.Tuple[int, int], str) -> None
        if string == 'Sequence' and 'Sequence[str]' in line:
            self.__sequence_str(line, start)

    def __disable_name_only(self, string, start):
        # type: (str, typing.Tuple[int, int]) -> None
        start_row, _ = start

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

    def __sequence_str(self, string, start):
        # type: (str, typing.Tuple[int, int]) -> None
        start_row, _ = start
        if self.RE_SEQUENCE_STRING.match(string):
            self.add_message('sequence-of-string', line=start_row)
