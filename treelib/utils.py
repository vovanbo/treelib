from typing import Hashable, Callable, Union, Tuple

from treelib.common import ASCIIMode
from treelib.exceptions import NodeNotFound


def get_label(node: 'Node', data_property: str, id_hidden: bool):
    result = getattr(node.data, data_property) \
        if data_property \
        else node.tag

    return result if id_hidden else f'{result}[{node.id}]'


def tree_printer_gen(tree: 'Tree', node_id: Hashable, level,
                     filtering: Callable[['Node'], bool], key, reverse: bool,
                     ascii_mode: ASCIIMode, is_last: list = None):
    dt_vline, dt_line_box, dt_line_cor = ascii_mode.value

    if is_last is None:
        is_last = []

    node_id = tree.root if node_id is None else node_id
    if not tree.contains(node_id):
        raise NodeNotFound(f"Node '{node_id}' is not in the tree")

    node = tree[node_id]

    if level == tree.ROOT:
        yield "", node
    else:
        leading = ''.join(dt_vline + ' ' * 3 if not x else ' ' * 4
                          for x in is_last[0:-1])
        lasting = dt_line_cor if is_last[-1] else dt_line_box
        yield leading + lasting, node

    if filtering(node) and node.expanded:
        children = [tree[n] for n in node.children if filtering(tree[n])]
        last_index = len(children) - 1

        if key:
            children_iter = sorted(children, key=key, reverse=reverse)
        elif reverse:
            children_iter = reversed(children)
        else:
            children_iter = children

        level += 1
        for index, child in enumerate(children_iter):
            is_last.append(index == last_index)
            for item in tree_printer_gen(tree, child.id, level, filtering,
                                         key, reverse, ascii_mode, is_last):
                yield item
            is_last.pop()


def print_backend(tree: 'Tree', node_id: Hashable = None, level=None,
                  id_hidden: bool = True,
                  filtering: Callable[['Node'], bool] = None,
                  key=None, reverse: bool = False,
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
    key_func = (lambda x: x) if key is None else key
    filtering = (lambda x: True) if filtering is None else filtering

    if level is None:
        level = tree.ROOT

    ascii_mode = (
        ascii_mode if isinstance(ascii_mode, ASCIIMode)
        else ASCIIMode[ascii_mode]
    )

    # iter with func
    for pre, node in tree_printer_gen(tree, node_id, level, filtering, key_func,
                                      reverse, ascii_mode):
        label = get_label(node, data_property, id_hidden)
        func('{0}{1}'.format(pre, label))
