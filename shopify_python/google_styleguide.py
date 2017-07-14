import re
import typing  # pylint: disable=unused-import

import astroid  # pylint: disable=unused-import
import shopify_python.ast
import six

from pylint import checkers
from pylint import interfaces
from pylint import lint  # pylint: disable=unused-import
from pylint import utils


def register_checkers(linter):  # type: (lint.PyLinter) -> None
    """Register checkers."""
    linter.register_checker(GoogleStyleGuideChecker(linter))


class GoogleStyleGuideChecker(checkers.BaseChecker):
    """
    Pylint checker for the Google Python Style Guide.

    See https://google.github.io/styleguide/pyguide.html

    Checks that can't be implemented include:
      - When capturing an exception, use as rather than a comma

    Checks that are already covered by Pylint include:
      - Never use catch-all 'except:' statements, or 'catch Exception' (bare-except, broad-except)
      - Do not use mutable objects as default values in the function or method definition (dangerous-default-value)
      - Do not terminate your lines with semi-colons and
        do not use semi-colons to put two commands on the same line. (unnecessary-semicolon, multiple-statements)
    """
    __implements__ = (interfaces.IAstroidChecker,)

    name = 'google-styleguide-checker'

    msgs = {
        'C6001': ('%(child)s is not a module or cannot be imported',
                  'import-modules-only',
                  'Only import packages or modules and ensure that they are installed.'),
        'C6002': ('%(module)s imported relatively',
                  'import-full-path',
                  'Import modules using their absolute names.'),
        'C6003': ('%(name)s declared at the module level (i.e. global)',
                  'global-variable',
                  'Avoid global variables in favor of class variables.'),
        'C6004': ('Raised two-argument exception',
                  'two-arg-exception',
                  "Use either raise Exception('message') or raise Exception."),
        'C6005': ('Raised deprecated string-exception',
                  'string-exception',
                  "Use either raise Exception('message') or raise Exception."),
        'C6006': ('Caught StandardError',
                  'catch-standard-error',
                  "Don't catch StandardError."),
        'C6007': ('Try body has %(found)i nodes',
                  'try-too-long',
                  "The larger the 'try' body size, the more likely that an unexpected exception will be raised."),
        'C6008': ('Except body has %(found)i nodes',
                  'except-too-long',
                  "The larger the 'except' body size, the more likely that an exception will be raised during "
                  "exception handling."),
        'C6009': ('Finally body has %(found)i nodes',
                  'finally-too-long',
                  "The larger the 'finally' body size, the more likely that an exception will be raised during "
                  "resource cleanup activities."),
        'C6010': ('Statement imports multiple items from %(module)s',
                  'multiple-import-items',
                  'Multiple imports usually result in noisy and potentially conflicting git diffs. To alleviate, '
                  'separate imports into one item per line.'),
        'C6011': ('Lambda has %(found)i nodes',
                  'use-simple-lambdas',
                  "Okay to use them for one-liners. If the code inside the lambda function is any longer than a "
                  "certain length, it's probably better to define it as a regular (nested) function."),
        'C6012': ('Multiple generators in list comprehension',
                  'complex-list-comp',
                  "Complicated list comprehensions or generator expressions can be hard to read; "
                  "don't use multiple 'for' keywords"),
        'C6013': ('Use Conditional Expressions for one-liners, for example x = 1 if cond else 2.',
                  'cond-expr',
                  "Conditional expressions are mechanisms that provide a shorter syntax for if statements. "
                  "For example: x = 1 if cond else 2. "
                  "Conditional Expressions okay to use for one-liners. "
                  "In other cases prefer to use a complete if statement. "),
        'C6014': ('Prefer operator module function %(op)s to lambda function',
                  'lambda-func',
                  "For common operations like multiplication, use the functions from the operator module"
                  "instead of lambda functions. For example, prefer operator.mul to lambda x, y: x * y."),
    }

    options = (
        ('ignore-module-import-only', {
            'default': ('__future__',),
            'type': 'csv',
            'help': 'List of top-level module names separated by comma.'}),
        ('max-try-nodes', {
            'default': 25,
            'type': 'int',
            'help': 'Number of AST nodes permitted in a try-block'}),
        ('max-except-nodes', {
            'default': 23,
            'type': 'int',
            'help': 'Number of AST nodes permitted in an except-block'}),
        ('max-finally-nodes', {
            'default': 13,
            'type': 'int',
            'help': 'Number of AST nodes permitted in a finally-block'}),
        ('max-lambda-nodes', {
            'default': 15,
            'type': 'int',
            'help': 'Number of AST nodes permitted in a lambda'}),
    )

    UNARY_OPERATORS = {
        "~": "invert",
        "-": "neg",
        "not": "not_",
        "+": "pos"
    }

    BINARY_OPERATORS = {
        "+": "add",
        "-": "sub",
        "*": "mul",
        "/": "truediv",
        "**": "pow",
        "%": "modulo",
        "<": "lt",
        "<=": "le",
        "==": "eq",
        "!=": "ne",
        ">=": "ge",
        ">": "gt",
        "is": "is"
    }

    def visit_assign(self, node):  # type: (astroid.Assign) -> None
        self.__avoid_global_variables(node)

    def visit_excepthandler(self, node):  # type: (astroid.ExceptHandler) -> None
        self.__dont_catch_standard_error(node)

    def visit_lambda(self, node):  # type: (astroid.Lambda) -> None
        self.__use_simple_lambdas(node)
        self.__lambda_func(node)

    def visit_listcomp(self, node):  # type: (astroid.ListComp) -> None
        self.__use_simple_list_comp(node)

    def visit_tryexcept(self, node):  # type: (astroid.TryExcept) -> None
        self.__minimize_code_in_try_except(node)

    def visit_tryfinally(self, node):  # type: (astroid.TryFinally) -> None
        self.__minimize_code_in_finally(node)

    def visit_importfrom(self, node):  # type: (astroid.ImportFrom) -> None
        self.__import_modules_only(node)
        self.__import_full_path_only(node)
        self.__limit_one_import(node)

    def visit_raise(self, node):  # type: (astroid.Raise) -> None
        self.__dont_use_archaic_raise_syntax(node)

    def visit_if(self, node):
        self.__use_cond_expr(node)  # type: (astroid.If) -> None

    @staticmethod
    def __get_module_names(node):  # type: (astroid.ImportFrom) -> typing.Generator[str, None, None]
        for name in node.names:
            name, _ = name
            yield '.'.join((node.modname, name))  # Rearrange "from x import y" as "import x.y"

    def __import_modules_only(self, node):  # type: (astroid.ImportFrom) -> None
        """Use imports for packages and modules only."""
        matches_ignored_module = any((node.modname.startswith(module_name) for module_name in
                                      self.config.ignore_module_import_only))  # pylint: disable=no-member
        if not node.level and not matches_ignored_module:
            # Walk up the parents until we hit one that can import a module (e.g. a module)
            parent = node.parent
            while not hasattr(parent, 'import_module'):
                parent = parent.parent

            # Warn on each imported name (yi) in "from x import y1, y2, y3"
            for child_module in self.__get_module_names(node):
                args = {'child': child_module}
                try:
                    parent.import_module(child_module)
                except astroid.exceptions.AstroidImportError as building_exception:
                    if str(building_exception).startswith('Failed to import module'):
                        self.add_message('import-modules-only', node=node, args=args)
                    else:
                        raise

    def __import_full_path_only(self, node):  # type: (astroid.ImportFrom) -> None
        """Import each module using the full pathname location of the module."""
        if node.level:
            for child_module in self.__get_module_names(node):
                self.add_message('import-full-path', node=node, args={'module': child_module})

    def __limit_one_import(self, node):  # type: (astroid.ImportFrom) -> None
        """Only one item imported per line."""
        if len(node.names) > 1:
            self.add_message('multiple-import-items', node=node, args={'module': node.modname})

    def __avoid_global_variables(self, node):  # type: (astroid.Assign) -> None
        """Avoid global variables."""

        def check_assignment(node):
            if utils.get_global_option(self, 'class-rgx').match(node.name):
                return  # Type definitions are allowed if they assign to a class name

            if utils.get_global_option(self, 'const-rgx').match(node.name) or \
               re.match('^__[a-z]+__$', node.name):
                return  # Constants are allowed

            self.add_message('global-variable', node=node, args={'name': node.name})

        # Is this an assignment happening within a module? If so report on each assignment name
        # whether its in a tuple or not
        if isinstance(node.parent, astroid.Module):
            for target in node.targets:
                if hasattr(target, 'elts'):
                    for elt in target.elts:
                        check_assignment(elt)
                elif hasattr(target, 'name'):
                    check_assignment(target)

    def __dont_use_archaic_raise_syntax(self, node):  # type: (astroid.Raise) -> None
        """Don't use the two-argument form of raise or the string raise"""
        children = list(node.get_children())
        if len(children) > 1 and not isinstance(children[1], astroid.Name):
            self.add_message('two-arg-exception', node=node)
        elif(len(children) == 1 and isinstance(children[0], astroid.Const) and
             isinstance(children[0].value, six.string_types)):
            self.add_message('string-exception', node=node)

    def __dont_catch_standard_error(self, node):  # type: (astroid.ExceptHandler) -> None
        """
        Never use catch-all 'except:' statements, or catch Exception or StandardError.

        Pylint already handles bare-except and broad-except (for Exception).
        """
        if hasattr(node.type, 'name') and node.type.name == 'StandardError':
            self.add_message('catch-standard-error', node=node)

    def __minimize_code_in_try_except(self, node):  # type: (astroid.TryExcept) -> None
        """Minimize the amount of code in a try/except block."""
        try_body_nodes = sum((shopify_python.ast.count_tree_size(child) for child in node.body))
        if try_body_nodes > self.config.max_try_nodes:  # pylint: disable=no-member
            self.add_message('try-too-long', node=node, args={'found': try_body_nodes})
        for handler in node.handlers:
            except_nodes = shopify_python.ast.count_tree_size(handler)
            if except_nodes > self.config.max_except_nodes:  # pylint: disable=no-member
                self.add_message('except-too-long', node=handler, args={'found': except_nodes})

    def __minimize_code_in_finally(self, node):  # type: (astroid.TryFinally) -> None
        """Minimize the amount of code in a finally block."""
        finally_body_nodes = sum((shopify_python.ast.count_tree_size(child) for child in node.finalbody))
        if finally_body_nodes > self.config.max_finally_nodes:  # pylint: disable=no-member
            self.add_message('finally-too-long', node=node, args={'found': finally_body_nodes})

    def __use_simple_lambdas(self, node):  # type: (astroid.Lambda) -> None
        lambda_nodes = shopify_python.ast.count_tree_size(node)
        if lambda_nodes > self.config.max_lambda_nodes:  # pylint: disable=no-member
            self.add_message('use-simple-lambdas', node=node, args={'found': lambda_nodes})

    def __use_simple_list_comp(self, node):  # type: (astroid.ListComp) -> None
        """List comprehensions are okay to use for simple cases."""
        if len(node.generators) > 1:
            self.add_message('complex-list-comp', node=node)

    def __use_cond_expr(self, node):  # type: (astroid.If) -> None
        """Only one liner conditional expressions"""

        if len(node.body) == 1 and len(node.orelse) == 1:
            if (isinstance(node.body[0], astroid.Assign) and
                    isinstance(node.body[0].targets[0], astroid.AssignName) and
                    isinstance(node.orelse[0], astroid.Assign) and
                    isinstance(node.orelse[0].targets[0], astroid.AssignName)):
                if_body_name = node.body[0].targets[0].name
                else_body_name = node.orelse[0].targets[0].name
                if if_body_name == else_body_name:
                    self.add_message('cond-expr', node=node)

    def __lambda_func(self, node):  # type: (astroid.Lambda) -> None
        """Prefer Operator Function to Lambda Functions"""

        if isinstance(node.body, astroid.UnaryOp):
            operator = self.UNARY_OPERATORS[node.body.op]
            argname = node.args.args[0].name
            if operator and not isinstance(node.body.operand, astroid.BinOp) and argname is node.body.operand.name:
                varname = node.body.operand.name
                lambda_fun = "lambda " + varname + ": " + node.body.op + " " + varname
                op_fun = "operator." + operator
                self.add_message('lambda-func', node=node, args={'op': op_fun, 'lambda_fun': lambda_fun})
        elif isinstance(node.body, astroid.BinOp):
            if shopify_python.ast.count_tree_size(node.body) == 3 and len(node.args.args) == 2:
                node = node.body
                operator = self.BINARY_OPERATORS[node.op]
                if operator:
                    left = str(node.left.value) if node.left.name == 'int' else node.left.name
                    right = str(node.right.value) if node.right.name == 'int' else node.right.name
                    lambda_fun = "lambda " + left + ', ' + right + ": " + " ".join([left, node.op, right])
                    op_fun = "operator." + operator
                    self.add_message('lambda-func', node=node, args={'op': op_fun, 'lambda_fun': lambda_fun})
        elif isinstance(node.body, astroid.Compare):
            if shopify_python.ast.count_tree_size(node.body) == 3 and len(node.args.args) == 2:
                node = node.body
                operator = self.BINARY_OPERATORS[node.ops[0][0]]
                if operator:
                    left = str(node.left.value) if node.left.name == 'int' else node.left.name
                    right = node.ops[0][1].name
                    lambda_fun = "lambda " + left + ', ' + right + ": " + " ".join([left, node.ops[0][0], right])
                    op_fun = "operator." + operator
                    self.add_message('lambda-func', node=node, args={'op': op_fun, 'lambda_fun': lambda_fun})
