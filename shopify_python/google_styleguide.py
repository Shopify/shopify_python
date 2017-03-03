import importlib

import astroid  # pylint: disable=unused-import
import six

from pylint import checkers, interfaces


def register_checkers(linter):  # type: (astroid.ImportFrom) -> None
    """Register checkers."""
    linter.register_checker(GoogleStyleGuideChecker(linter))


class GoogleStyleGuideChecker(checkers.BaseChecker):
    """
    Pylint checker for the Google Python Style Guide.

    See https://google.github.io/styleguide/pyguide.html
    """
    __implements__ = (interfaces.IAstroidChecker,)

    name = 'google-styleguide-checker'

    msgs = {
        'C9901': ('Imported an object that is not a package or module',
                  'import-modules-only',
                  'Use imports for packages and modules only'),
        'C9902': ('Imported using a partial path',
                  'import-full-path',
                  'Import each module using the full pathname location of the module.'),
        'C9903': ('Variable declared at the module level (i.e. global)',
                  'global-variable',
                  'Avoid global variables in favor of class variables'),
        'C9904': ('Raised two-argument exception',
                  'two-arg-exception',
                  "Use either raise Exception('message') or raise Exception"),
        'C9905': ('Raised deprecated string-exception',
                  'string-exception',
                  "Use either raise Exception('message') or raise Exception"),
        'C9906': ('Caught StandardError',
                  'catch-standard-error',
                  "Don't catch broad exceptions"),
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
        def can_import(module):
            try:
                importlib.import_module(module)
                return True
            except ImportError:
                return False

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
        if isinstance(node.parent, astroid.Module):
            self.add_message('global-variable', node=node)

    def __dont_use_archaic_raise_syntax(self, node):  # type: (astroid.Raise) -> None
        """Don't use the two-argument form of raise or the string raise"""
        children = list(node.get_children())
        if len(children) > 1:
            self.add_message('two-arg-exception', node=node)
        elif len(children) == 1 and isinstance(children[0], six.string_types):
            self.add_message('string-exception', node=node)

    def __dont_catch_standard_error(self, node):  # type: (astroid.ExceptHandler) -> None
        """
        Never use catch-all 'except:' statements, or catch Exception or StandardError.

        Pylint already handles bare-except and broad-except (for Exception).
        """
        if node.type.name == 'StandardError':
            self.add_message('catch-standard-error', node=node)

        # TODO Exceptions are allowed but must be used carefully.
        #   - Never use catch-all except: statements, or catch Exception or StandardError,
        #     - Covered by bare-except, broad-except, but not StandardError
        #   - When capturing an exception, use as rather than a comma. For example:
        #   - Minimize the amount of code in a try/except block.

    # TODO List comprehensions are okay to use for simple cases.
    # def visit_comprehension, check parent, it it contains multiple generators then that's bad

    # TODO Use default iterators and operators for types that support them, like lists, dictionaries, and files.

    # TODO Lambdas are okay for one-liners.
    # TODO Conditional expressions are okay for one-liners.

    # TODO Do not use mutable objects as default values in the function or
    # method definition. (is this covered by pylint already?)

    # TODO Use properties for accessing or setting data where you would
    # normally have used simple, lightweight accessor or setter methods.

    # TODO Use the "implicit" false if at all possible.

    # TODO Use string methods instead of the string module where possible. (Covered by pylint)

    # TODO Avoid fancy features like metaclasses, access to bytecode,
    # on-the-fly compilation, dynamic inheritance, object reparenting, import
    # hacks, reflection, modification of system internals, etc.

    # TODO Shebang lines shoul dbe of the form  #!/usr/bin/env python with an optional single digit 2 or 3 suffix

    # TODO If a class inherits from no other base classes, explicitly inherit from object.  (already covered by pylint?)
