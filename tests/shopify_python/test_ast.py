import astroid

from shopify_python import ast


def test_count_tree_size():
    root = astroid.builder.parse("""
    def test(x, y):
        return x * y if x > 5 else 0
    """)
    assert ast.count_tree_size(root) == 14
