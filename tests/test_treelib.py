#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
from treelib import Tree, Node
from treelib.exceptions import NodeNotFound, LoopError
import pytest


def test_tree(tree, copytree):
    assert isinstance(tree, Tree)
    assert isinstance(copytree, Tree)


def test_is_root(tree):
    assert tree.nodes['hárry'].is_root
    assert not tree.nodes['jane'].is_root


def test_paths_to_leaves(tree):
    paths = tree.paths_to_leaves()
    assert len(paths) == 2
    assert ['hárry', 'jane', 'diane'] in paths
    assert ['hárry', 'bill', 'george'] in paths


def test_nodes(tree):
    assert len(tree.nodes) == 5
    assert len(tree.all_nodes()) == 5
    assert tree.size() == 5
    assert tree.get_node("jane").tag == "Jane"
    assert tree["jane"].tag == "Jane"
    assert tree.contains("jane")
    assert "jane" in tree
    assert not tree.contains("alien")
    tree.create_node("Alien", "alien", parent="jane")
    assert tree.contains("alien")
    tree.remove_node("alien")
    assert not tree.contains('alien')


def test_getitem(tree):
    """Nodes can be accessed via getitem."""
    for node_id in tree.nodes:
        assert tree[node_id]

    # assert 'Node access should be possible via getitem.' in str(exc)

    with pytest.raises(NodeNotFound):
        assert tree['root']


def test_parent(tree):
    for nid in tree.nodes:
        if nid == tree.root:
            assert tree.parent(nid) is None
        else:
            assert tree.parent(nid) in tree.all_nodes()


def test_children(tree):
    for nid in tree.nodes:
        children = tree.is_branch(nid)
        for child in children:
            assert tree[child] in tree.all_nodes()
        children = tree.children(nid)
        for child in children:
            assert child in tree.all_nodes()

    with pytest.raises(NodeNotFound) as exc:
        assert tree.is_branch("alien")

    assert "Node 'alien' is not in the tree" in str(exc)


def test_remove_node(tree):
    tree.create_node("Jill", "jill", parent="george")
    tree.create_node("Mark", "mark", parent="jill")
    assert tree.remove_node("jill") == 2
    assert tree.get_node("jill") is None
    assert tree.get_node("mark") is None


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
    assert tree.depth(tree.get_node("mark")) == 4
    assert tree.depth(tree.get_node("jill")) == 3
    assert tree.depth(tree.get_node("george")) == 2
    assert tree.depth("jane") == 1
    assert tree.depth("bill") == 1
    assert tree.depth("hárry") == 0

    # Try getting Exception
    node = Node("Test One", "identifier 1")
    with pytest.raises(NodeNotFound):
        tree.depth(node)


def test_leaves(tree):
    leaves = tree.leaves()
    for nid in tree.expand_tree():
        assert tree[nid].is_leaf == (tree[nid] in leaves)

    leaves = tree.leaves(nid='jane')
    for nid in tree.expand_tree(node_id='jane'):
        assert tree[nid].is_leaf == (tree[nid] in leaves)


def test_link_past_node(tree):
    tree.create_node("Jill", "jill", parent="hárry")
    tree.create_node("Mark", "mark", parent="jill")
    assert "mark" not in tree.is_branch("hárry")

    tree.link_past_node("jill")
    assert "mark" in tree.is_branch("hárry")


def test_expand_tree(tree):
    # default config
    nodes = [nid for nid in tree.expand_tree()]
    assert len(nodes) == 5

    # expanding from specific node
    nodes = [nid for nid in tree.expand_tree(node_id="bill")]
    assert len(nodes) == 2

    # changing into width mode
    nodes = [nid for nid in tree.expand_tree(mode='width')]
    assert len(nodes) == 5

    # expanding by filters
    nodes = [nid for nid in tree.expand_tree(filter=lambda x: x.tag == "Bill")]
    assert len(nodes) == 0
    nodes = [nid for nid in tree.expand_tree(filter=lambda x: x.tag != "Bill")]
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
    for nid in ["hárry", "jane", "diane"]:
        assert nid in tree.rsearch("diane")


def test_subtree(tree):
    subtree_copy = Tree(tree.subtree("jane"), deep=True)
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


def test_tree_print(capsys, tree, tree_as_string):
    tree.print()

    stdout, stderr = capsys.readouterr()
    assert stdout == tree_as_string


def test_all_nodes_itr():
    """
    tests: Tree.all_nodes_iter
    Added by: William Rusnack
    """
    new_tree = Tree()
    assert not new_tree.all_nodes_iter()
    nodes = [new_tree.create_node('root_node'),
             new_tree.create_node('second', parent=new_tree.root)]
    for nd in new_tree.all_nodes_iter():
        assert nd in nodes


def test_filter_nodes():
    """
    tests: Tree.filter_nodes
    Added by: William Rusnack
    """
    new_tree = Tree()

    assert not tuple(new_tree.filter_nodes(lambda n: True))

    nodes = [new_tree.create_node('root_node'),
             new_tree.create_node('second', parent=new_tree.root)]

    assert tuple(new_tree.filter_nodes(lambda n: False)) == ()
    assert tuple(new_tree.filter_nodes(lambda n: n.is_root)) == (nodes[0],)
    assert tuple(new_tree.filter_nodes(lambda n: not n.is_root)) == \
           (nodes[1],)
    assert set(new_tree.filter_nodes(lambda n: True))
    assert set(nodes)


def test_loop():
    tree = Tree()
    tree.create_node('a', 'a')
    tree.create_node('b', 'b', parent='a')
    tree.create_node('c', 'c', parent='b')
    tree.create_node('d', 'd', parent='c')
    try:
        tree.move_node('b', 'd')
    except LoopError:
        pass
