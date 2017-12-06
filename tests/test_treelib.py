#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest

from ttree import Tree, Node
from ttree.exceptions import NodeNotFound, LoopError


def test_tree(tree, copytree):
    assert isinstance(tree, Tree)
    assert isinstance(copytree, Tree)


def test_is_root(tree):
    assert tree['hárry'].is_root
    assert not tree['jane'].is_root


def test_paths_to_leaves(tree):
    paths = tree.paths_to_leaves
    assert len(paths) == 2
    assert ['hárry', 'jane', 'diane'] in paths
    assert ['hárry', 'bill', 'george'] in paths


def test_nodes(tree):
    assert len(tree) == 5
    assert len(tree.values()) == 5
    assert tree.size() == 5
    assert tree.get("jane").tag == "Jane"
    assert tree["jane"].tag == "Jane"
    assert "jane" in tree
    assert "alien" not in tree
    tree.create_node("Alien", "alien", parent="jane")
    assert "alien" in tree
    tree.remove_node("alien")
    assert "alien" not in tree


def test_getitem(tree):
    """Nodes can be accessed via getitem."""
    for node_id in tree:
        assert tree[node_id]

    # assert 'Node access should be possible via getitem.' in str(exc)

    with pytest.raises(NodeNotFound) as exc:
        assert tree['root']

    assert "Node 'root' is not in the tree" in str(exc)


def test_parent(tree):
    for node_id in tree:
        if node_id == tree.root:
            assert tree.parent(node_id) is None
        else:
            assert tree.parent(node_id) in tree.values()


def test_children(tree):
    for node_id in tree:
        children = tree.is_branch(node_id)
        for child in children:
            assert tree[child] in tree.values()
        children = tree.children(node_id)
        for child in children:
            assert child in tree.values()

    with pytest.raises(NodeNotFound) as exc:
        assert tree.is_branch("alien")

    assert "Node 'alien' is not in the tree" in str(exc)


def test_remove_node(tree):
    tree.create_node("Jill", "jill", parent="george")
    tree.create_node("Mark", "mark", parent="jill")
    assert tree.remove_node("jill") == 2
    assert tree.get("jill") is None
    assert tree.get("mark") is None


def test_depth(tree):
    # Try getting the level of this tree
    assert tree.depth() == 2
    tree.create_node("Jill", "jill", parent="george")
    assert tree.depth() == 3
    tree.create_node("Mark", "mark", parent="jill")
    assert tree.depth() == 4

    # Try getting the level of the node
    """
    tree.print()
    Hárry
    |___ Bill
    |    |___ George
    |         |___ Jill
    |              |___ Mark
    |___ Jane
    |    |___ Diane
    """
    assert tree.depth(tree.get("mark")) == 4
    assert tree.depth(tree.get("jill")) == 3
    assert tree.depth(tree.get("george")) == 2
    assert tree.depth("jane") == 1
    assert tree.depth("bill") == 1
    assert tree.depth("hárry") == 0

    # Try getting Exception
    node = Node("Test One", "identifier 1")
    with pytest.raises(NodeNotFound):
        tree.depth(node)


def test_leaves(tree):
    leaves = tree.leaves()
    for node_id in tree.expand_tree():
        assert tree[node_id].is_leaf == (tree[node_id] in leaves)

    leaves = tree.leaves(node_id='jane')
    for node_id in tree.expand_tree(node_id='jane'):
        assert tree[node_id].is_leaf == (tree[node_id] in leaves)


def test_link_past_node(tree):
    tree.create_node("Jill", "jill", parent="hárry")
    tree.create_node("Mark", "mark", parent="jill")
    assert "mark" not in tree.is_branch("hárry")

    tree.link_past_node("jill")
    assert "mark" in tree.is_branch("hárry")


def test_expand_tree(tree):
    # default config
    nodes = [n for n in tree.expand_tree()]
    assert len(nodes) == 5

    # expanding from specific node
    nodes = [n for n in tree.expand_tree(node_id="bill")]
    assert len(nodes) == 2

    # changing into width mode
    nodes = [n for n in tree.expand_tree(mode='width')]
    assert len(nodes) == 5

    # expanding by filters
    nodes = \
        [n for n in tree.expand_tree(filtering=lambda x: x.tag == "Bill")]
    assert len(nodes) == 0
    nodes = \
        [n for n in tree.expand_tree(filtering=lambda x: x.tag != "Bill")]
    assert len(nodes) == 3


def test_move_node(tree):
    diane_parent = tree.parent("diane")
    tree.move_node("diane", "bill")
    assert "diane" in tree.is_branch("bill")
    tree.move_node("diane", diane_parent.id)


def test_paste_tree(tree):
    new_tree = Tree()
    new_tree.create_node("Jill", "jill")
    new_tree.create_node("Mark", "mark", parent="jill")
    tree.paste("jane", new_tree)
    assert "jill" in tree.is_branch("jane")
    tree.remove_node("jill")


def test_rsearch(tree):
    for node_id in ["hárry", "jane", "diane"]:
        assert node_id in tree.rsearch("diane")


def test_subtree(tree):
    subtree_copy = Tree(tree.subtree("jane"), deepcopy=True)
    assert subtree_copy.parent("jane") is None
    subtree_copy["jane"].tag = "Sweetie"
    assert tree["jane"].tag == "Jane"
    assert subtree_copy.level("diane") == 1
    assert subtree_copy.level("jane") == 0
    assert tree.level("jane") == 1


def test_remove_subtree(tree):
    subtree_shallow = tree.remove_subtree("jane")
    assert "jane" not in tree.is_branch("hárry")
    tree.paste("hárry", subtree_shallow)
    assert "jane" in tree.is_branch("hárry")


def test_to_json(tree):
    # assertEqual.__self__.maxDiff = None
    assert tree.to_json() == (
        '{"H\\u00e1rry": {"children": [{"Bill": {"children": ["George"]}}, '
        '{"Jane": {"children": ["Diane"]}}]}}'
    )
    assert tree.to_json(with_data=True) == (
        '{"H\\u00e1rry": {"children": [{"Bill": {"children": '
        '[{"George": {"data": null}}], "data": null}}, '
        '{"Jane": {"children": [{"Diane": {"data": null}}], "data": null}}], '
        '"data": null}}'
    )


def test_siblings(tree):
    assert not tree.siblings("hárry")
    assert tree.siblings("jane")[0].id == "bill"


def test_tree_data(tree):
    class Flower(object):
        def __init__(self, color):
            self.color = color

    tree.create_node("Jill", "jill", parent="jane", data=Flower("white"))
    assert tree["jill"].data.color == "white"
    tree.remove_node("jill")


def test_tree_print_data_property(capsys):
    new_tree = Tree()
    new_tree.print()

    stdout, stderr = capsys.readouterr()
    assert stdout == 'Tree is empty\n'

    class Flower(object):
        def __init__(self, color):
            self.color = color

    new_tree.create_node("Jill", "jill", data=Flower("white"))
    new_tree.print(data_property="color")

    stdout, stderr = capsys.readouterr()
    assert stdout == 'white\n'


def test_level(tree):
    assert tree.level('hárry') == 0
    depth = tree.depth()
    assert tree.level('diane') == depth
    assert tree.level('diane', lambda x: x.id != 'jane') == depth - 1


def test_size(tree):
    assert tree.size(level=2) == 2
    assert tree.size(level=1) == 2
    assert tree.size(level=0) == 1


def test_tree_to_string(tree, tree_as_string):
    assert str(tree) == tree_as_string


def test_tree_print(capsys, tree):
    tree.print()

    stdout, stderr = capsys.readouterr()
    assert stdout == """\
Hárry
├── Jane
│   └── Diane
└── Bill
    └── George
"""


def test_tree_iteration():
    new_tree = Tree()
    assert not new_tree.values()
    nodes = [new_tree.create_node('root_node'),
             new_tree.create_node('second', parent=new_tree.root)]
    for nd in new_tree.values():
        assert nd in nodes


def test_filter_nodes():
    new_tree = Tree()

    assert not tuple(filter(lambda n: True, new_tree.values()))

    nodes = [new_tree.create_node('root_node'),
             new_tree.create_node('second', parent=new_tree.root)]

    assert tuple(filter(lambda n: False, new_tree.values())) == ()
    assert tuple(filter(lambda n: n.is_root, new_tree.values())) == (nodes[0],)
    assert tuple(filter(lambda n: not n.is_root, new_tree.values())) == \
           (nodes[1],)
    assert set(filter(lambda n: True, new_tree.values()))
    assert set(nodes)


def test_loop():
    tree = Tree()
    tree.create_node('a', 'a')
    tree.create_node('b', 'b', parent='a')
    tree.create_node('c', 'c', parent='b')
    tree.create_node('d', 'd', parent='c')

    with pytest.raises(LoopError):
        tree.move_node(source='b', destination='d')


def test_node_to_tree_link():
    tree = Tree()
    node_a = tree.create_node('a', 'a')
    assert node_a.tree is tree
    tree.create_node('b', 'b', parent='a')
    tree.create_node('c', 'c', parent='b')
    tree.create_node('d', 'd', parent='c')
    tree.remove_node(node_a.id)
    assert node_a.tree is None
