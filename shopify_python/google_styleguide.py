import importlib

import astroid  # pylint: disable=unused-import

from pylint import checkers, interfaces


def register_checkers(linter):  # type: (astroid.ImportFrom) -> None
    """Register checkers."""
    linter.register_checker(GoogleStyleGuideChecker(linter))


class GoogleStyleGuideChecker(checkers.BaseChecker):
    __implements__ = (interfaces.IAstroidChecker,)

    name = 'google-styleguide-checker'

    msgs = {
        'C9901': ('Imported an object that is not a package or module',
                  'import-modules-only',
                  'Use imports for packages and modules only.'),
        'C9902': ('Imported using a partial path',
                  'import-full-path',
                  'Import each module using the full pathname location of the module.')
    }

    def visit_importfrom(self, node):  # type: (astroid.ImportFrom) -> None
        self._import_modules_only(node)
        self._import_full_path_only(node)

    def _import_modules_only(self, node):  # type: (astroid.ImportFrom) -> None
        """
        Use imports for packages and modules only.

        See https://google.github.io/styleguide/pyguide.html?showone=Imports#Imports
        """
        def can_import(module):
            try:
                importlib.import_module(module)
                return True
            except ImportError:
                return False

        if not node.level and node.modname != '__future__':
            for name in node.names:
                # Try to rearrange "from x import y" as "import x.y" and import it as a module
                name, _ = name
                parent_module = node.modname
                child_module = '.'.join((node.modname, name))
                if can_import(parent_module) and not can_import(child_module):
                    self.add_message('import-modules-only', node=node)

    def _import_full_path_only(self, node):  # type: (astroid.ImportFrom) -> None
        """
        Import each module using the full pathname location of the module.

        See https://google.github.io/styleguide/pyguide.html?showone=Packages#Packages
        """
        if node.level:
            self.add_message('import-full-path', node=node)
