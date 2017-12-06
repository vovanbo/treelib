from typing import Hashable, Callable, Union

from ttree.common import ASCIIMode, TraversalMode


def tree_printer_gen(tree, node_id: Hashable, filtering=None, key=None,
                     reverse: bool = False,
                     ascii_mode: ASCIIMode = ASCIIMode.ex,
                     is_last: list = None, level: int = 0):
    """
    Generate elements of existing tree.

    :param ~ttree.Tree tree: Tree instance
    :param node_id: Traversal root node ID
    :param filtering: Filtering callable
    :param key: Sorting key callable
    :param reverse: Reverse mode
    :param ascii_mode: ASCII mode
    :param is_last: Recursion tail flag
    :param level: Current level of tree in recursion
    """
    c_line, c_branch, c_corner = ascii_mode.value

    if is_last is None:
        is_last = []

    node_id = tree.root if node_id is None else node_id
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
            children = (n for n in sorted(children, key=key, reverse=reverse))
        elif reverse:
            children = (n for n in reversed(list(children)))

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


def get_label(node, data_property: str, id_hidden: bool):
    """
    Get label of node.

    :param ~ttree.Node node: Tree node instance
    :param data_property: Data property name
    :param id_hidden: Is ID hidden?
    :return:
    """
    result = getattr(node.data, data_property) \
        if data_property \
        else node.tag

    return result if id_hidden else f'{result}[{node.id}]'


def print_tree(tree, node_id: Hashable = None, id_hidden: bool = True,
               filtering=None, key=None, reverse: bool = False,
               ascii_mode: Union[ASCIIMode, str] = ASCIIMode.ex,
               data_property: str = None, func: Callable = None):
    """
    Another implementation of printing tree using Stack Print tree structure
    in hierarchy style.

    For example:

    .. code-block:: text

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

    :param ~ttree.Tree tree: Tree instance
    :param node_id: Traversal root node ID
    :param id_hidden: Is ID hidden?
    :param filtering: Filtering callable
    :param key: Sorting key callable
    :param reverse: Reverse mode?
    :param ascii_mode: ASCII mode
    :param data_property: Data property name
    :param func: Printer function callable
    """
    ascii_mode = (
        ascii_mode if isinstance(ascii_mode, ASCIIMode)
        else ASCIIMode[ascii_mode]
    )

    result = (
        f'{pre}{get_label(node, data_property, id_hidden)}'
        for pre, node in tree_printer_gen(tree, node_id, filtering, key,
                                          reverse, ascii_mode)
    )

    if func is not None and callable(func):
        for s in result:
            func(s)
    else:
        return '\n'.join(s for s in result) + '\n'


def export_to_dot(tree, filename: str, shape='circle', graph='digraph'):
    """
    Export the tree in the DOT format of the Graphviz software.

    .. seealso::

        * `Graphviz <http://www.graphviz.org>`_
        * `DOT Language <http://www.graphviz.org/content/dot-language>`_

    :param ~ttree.Tree tree: Tree instance
    :param filename: Export file name
    :param shape: Shape of tree node in DOT
    :param graph: Graph type in DOT
    """
    nodes, connections = [], []

    if tree:
        for node in tree.expand_tree(mode=TraversalMode.WIDTH):
            node_id = tree[node].id
            nodes.append(
                f'"{node_id}" [label="{tree[node].tag}", shape={shape}]'
            )

            connections.extend(
                [f'"{node_id}" -> "{c.id}"' for c in tree.children(node_id)]
            )

    # write nodes and connections to dot format
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f'{graph} tree {{\n')

        for node in nodes:
            f.write(f'\t{node}\n')

        f.write('\n')

        for child in connections:
            f.write(f'\t{child}\n')

        f.write('}')
