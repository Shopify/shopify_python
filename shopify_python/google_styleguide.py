import typing  # pylint: disable=unused-import

import astroid  # pylint: disable=unused-import
import six

from pylint import checkers
from pylint import interfaces
from pylint import lint  # pylint: disable=unused-import


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
        'C2601': ('%(child)s is not a module or cannot be imported',
                  'import-modules-only',
                  'Install %(child)s or only import packages or modules from it'),
        'C2602': ('%(module)s imported relatively',
                  'import-full-path',
                  'Import %(module)s using the absolute name.'),
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

    options = (
         ('ignore-module-import-only', {
             'default': ('__future__',),
             'type': 'csv',
             'help': 'List of top-level module names separated by comma.'}),
    )
    
    def visit_assign(self, node):  # type: (astroid.Assign) -> None
        self.__avoid_global_variables(node)

    def visit_excepthandler(self, node):  # type: (astroid.ExceptHandler) -> None
        self.__dont_catch_standard_error(node)

    def visit_importfrom(self, node):  # type: (astroid.ImportFrom) -> None
        self.__import_modules_only(node)
        self.__import_full_path_only(node)

    def visit_raise(self, node):  # type: (astroid.Raise) -> None
        self.__dont_use_archaic_raise_syntax(node)

    @staticmethod
    def __get_module_names(node):  # type: (astroid.ImportFrom) -> typing.Generator[str, None, None]
        for name in node.names:
            name, _ = name
            yield '.'.join((node.modname, name))  # Rearrange "from x import y" as "import x.y"

    def __import_modules_only(self, node):  # type: (astroid.ImportFrom) -> None
        """Use imports for packages and modules only."""
        matches_ignored_module = any(
            (node.modname.startswith(module_name) for module_name in self.config.ignore_module_import_only))
        if not node.level and not matches_ignored_module:
            # Walk up the parents until we hit one that can import a module (e.g. a module)
            parent = node.parent
            while not hasattr(parent, 'import_module'):
                parent = parent.parent

            # Warn on each imported name (yi) in "from x import y1, y2, y3"
            for child_module in self.__get_module_names(node):
                try:
                    parent.import_module(child_module)
                except astroid.exceptions.AstroidBuildingException as building_exception:
                    if str(building_exception).startswith('Unable to load module'):
                        self.add_message('import-modules-only', node=node, args={'child': child_module})
                    else:
                        raise

    def __import_full_path_only(self, node):  # type: (astroid.ImportFrom) -> None
        """Import each module using the full pathname location of the module."""
        if node.level:
            for child_module in self.__get_module_names(node):
                self.add_message('import-full-path', node=node, args={'module': child_module})

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
