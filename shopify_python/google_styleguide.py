import sys

import astroid  # pylint: disable=unused-import
import six

from pylint import checkers
from pylint import interfaces
from pylint import lint  # pylint: disable=unused-import


if sys.version_info >= (3, 4):
    import importlib.util  # pylint: disable=no-name-in-module,import-error
else:
    import importlib


def register_checkers(linter):  # type: (lint.PyLinter) -> None
    """Register checkers."""
    linter.register_checker(GoogleStyleGuideChecker(linter))


class GoogleStyleGuideChecker(checkers.BaseChecker):
    """
    Pylint checker for the Google Python Style Guide.

    See https://google.github.io/styleguide/pyguide.html

    Checks that can't be implemented include:
      - When capturing an exception, use as rather than a comma
    """
    __implements__ = (interfaces.IAstroidChecker,)

    name = 'google-styleguide-checker'

    msgs = {
        'C2601': ('Imported an object that is not a package or module',
                  'import-modules-only',
                  'Use imports for packages and modules only'),
        'C2602': ('Imported using a partial path',
                  'import-full-path',
                  'Import each module using the full pathname location of the module.'),
        'C2603': ('Variable declared at the module level (i.e. global)',
                  'global-variable',
                  'Avoid global variables in favor of class variables'),
        'C2604': ('Raised two-argument exception',
                  'two-arg-exception',
                  "Use either raise Exception('message') or raise Exception"),
        'C2605': ('Raised deprecated string-exception',
                  'string-exception',
                  "Use either raise Exception('message') or raise Exception"),
        'C2606': ('Caught StandardError',
                  'catch-standard-error',
                  "Don't catch StandardError"),
    }

    def visit_assign(self, node):  # type: (astroid.Assign) -> None
        self.__avoid_global_variables(node)

    def visit_excepthandler(self, node):  # type: (astroid.ExceptHandler) -> None
        self.__dont_catch_standard_error(node)

    def visit_importfrom(self, node):  # type: (astroid.ImportFrom) -> None
        self.__import_modules_only(node)
        self.__import_full_path_only(node)

    def visit_raise(self, node):  # type: (astroid.Raise) -> None
        self.__dont_use_archaic_raise_syntax(node)

    def __import_modules_only(self, node):  # type: (astroid.ImportFrom) -> None
        """Use imports for packages and modules only."""

        if hasattr(self.linter, 'config') and 'import-modules-only' in self.linter.config.disable:
            return  # Skip if disable to avoid side-effects from importing modules

        def can_import(module_name):
            if sys.version_info >= (3, 4):
                try:
                    return bool(importlib.util.find_spec(module_name))
                except AttributeError:
                    return False  # Occurs when a module doesn't exist
                except ImportError:
                    return False  # Occurs when a module encounters an error during import
            else:
                try:
                    importlib.import_module(module_name)
                    return True
                except ImportError:
                    return False  # Occurs when a module doesn't exist or on error during import

        if not node.level and node.modname != '__future__':
            for name in node.names:
                name, _ = name
                parent_module = node.modname
                child_module = '.'.join((node.modname, name))  # Rearrange "from x import y" as "import x.y"
                if can_import(parent_module) and not can_import(child_module):
                    self.add_message('import-modules-only', node=node)

    def __import_full_path_only(self, node):  # type: (astroid.ImportFrom) -> None
        """Import each module using the full pathname location of the module."""
        if node.level:
            self.add_message('import-full-path', node=node)

    def __avoid_global_variables(self, node):  # type: (astroid.Assign) -> None
        """Avoid global variables."""
        # Is this an assignment happening within a module? If so report on each assignment name
        # whether its in a tuple or not
        if isinstance(node.parent, astroid.Module):
            for target in node.targets:
                if hasattr(target, 'elts'):
                    for elt in target.elts:
                        if elt.name != '__version__':
                            self.add_message('global-variable', node=elt)
                elif hasattr(target, 'name'):
                    if target.name != '__version__':
                        self.add_message('global-variable', node=target)

    def __dont_use_archaic_raise_syntax(self, node):  # type: (astroid.Raise) -> None
        """Don't use the two-argument form of raise or the string raise"""
        children = list(node.get_children())
        if len(children) > 1 and not isinstance(children[1], astroid.Name):
            self.add_message('two-arg-exception', node=node)
        elif len(children) == 1 and isinstance(children[0], six.string_types):
            self.add_message('string-exception', node=node)

    def __dont_catch_standard_error(self, node):  # type: (astroid.ExceptHandler) -> None
        """
        Never use catch-all 'except:' statements, or catch Exception or StandardError.

        Pylint already handles bare-except and broad-except (for Exception).
        """
        if hasattr(node.type, 'name') and node.type.name == 'StandardError':
            self.add_message('catch-standard-error', node=node)
