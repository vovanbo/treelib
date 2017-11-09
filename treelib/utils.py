from typing import Hashable, Callable, Union, Any

from treelib.common import ASCIIMode
from treelib.exceptions import NodeNotFound


def get_label(node: 'Node', data_property: str, id_hidden: bool):
    result = getattr(node.data, data_property) \
        if data_property \
        else node.tag

    return result if id_hidden else f'{result}[{node.id}]'


def tree_printer_gen(tree: 'Tree', node_id: Hashable,
                     filtering: Callable[['Node'], bool] = None,
                     key: Callable[['Node'], Any] = None,
                     reverse: bool = False,
                     ascii_mode: ASCIIMode = ASCIIMode.ex,
                     is_last: list = None, level: int = 0):
    c_line, c_branch, c_corner = ascii_mode.value

    if is_last is None:
        is_last = []

    node_id = tree.root if node_id is None else node_id
    if not tree.contains(node_id):
        raise NodeNotFound(f"Node '{node_id}' is not in the tree")

    node = tree[node_id]

    if level == 0:
        yield "", node
    else:
        leading = ''.join(c_line + ' ' * 3 if not x else ' ' * 4
                          for x in is_last[0:-1])
        lasting = c_corner if is_last[-1] else c_branch
        yield leading + lasting, node

    if node.expanded:
        if filtering is not None and not filtering(node):
            return

        children = (tree[n] for n in node.children)

        if filtering is not None:
            children = filter(filtering, children)

        if key is not None:
            children = sorted(children, key=key, reverse=reverse)
        elif reverse:
            children = reversed(children)

        level += 1
        current_child = next(children, None)
        while children and current_child is not None:
            next_child = next(children, None)
            is_last.append(next_child is None)
            for item in tree_printer_gen(tree, current_child.id,
                                         filtering, key, reverse, ascii_mode,
                                         is_last, level=level):
                yield item
            is_last.pop()
            current_child = next_child


def print_tree(tree: 'Tree', node_id: Hashable = None,
               id_hidden: bool = True,
               filtering: Callable[['Node'], bool] = None,
               key: Callable[['Node'], Any] = None, reverse: bool = False,
               ascii_mode: Union[ASCIIMode, str] = ASCIIMode.ex,
               data_property: str = None, func: Callable = print):
    """
    Another implementation of printing tree using Stack
    Print tree structure in hierarchy style.

    For example:
        Root
        |___ C01
        |    |___ C11
        |         |___ C111
        |         |___ C112
        |___ C02
        |___ C03
        |    |___ C31

    A more elegant way to achieve this function using Stack
    structure, for constructing the Nodes Stack push and pop nodes
    with additional level info.

    UPDATE: the @key @reverse is present to sort node at each
    level.
    """
    ascii_mode = (
        ascii_mode if isinstance(ascii_mode, ASCIIMode)
        else ASCIIMode[ascii_mode]
    )

    # iter with func
    for pre, node in tree_printer_gen(tree, node_id, filtering, key,
                                      reverse, ascii_mode):
        label = get_label(node, data_property, id_hidden)
        func(f'{pre}{label}')
