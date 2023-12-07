import astroid  # pylint: disable=unused-import


def count_tree_size(node):  # type: (astroid.NodeNG) -> int
    size = 1 if node else 0
    for child in node.get_children():
        size += count_tree_size(child)
    return size
