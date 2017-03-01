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
        if not node.level and node.modname != '__future__':
            for name in node.names:
                # Try to rearrange "from x import y" as "import x.y" and import it as a module
                name, _ = name
                module = '.'.join((node.modname, name))
                try:
                    importlib.import_module(module)
                except ImportError as import_error:
                    if str(import_error).startswith('No module named'):
                        self.add_message('import-modules-only', node=node)

    def _import_full_path_only(self, node):  # type: (astroid.ImportFrom) -> None
        """
        Import each module using the full pathname location of the module.

        See https://google.github.io/styleguide/pyguide.html?showone=Packages#Packages
        """
        if node.level:
            self.add_message('import-full-path', node=node)
