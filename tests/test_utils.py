#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from ttree import Tree
from ttree.utils import export_to_dot


def read_generated_output(filename):
    with open(filename, 'r', encoding='utf-8') as fp:
        return fp.read()


def test_export_to_dot(tree):
    export_to_dot(tree, 'tree.dot')
    expected = """\
digraph tree {
\t"hárry" [label="Hárry", shape=circle]
\t"bill" [label="Bill", shape=circle]
\t"jane" [label="Jane", shape=circle]
\t"george" [label="George", shape=circle]
\t"diane" [label="Diane", shape=circle]

\t"hárry" -> "jane"
\t"hárry" -> "bill"
\t"bill" -> "george"
\t"jane" -> "diane"
}"""

    assert os.path.isfile('tree.dot')
    generated = read_generated_output('tree.dot')

    assert generated == expected
    os.remove('tree.dot')


def test_export_to_dot_empty_tree():
    empty_tree = Tree()
    export_to_dot(empty_tree, 'tree.dot')

    expected = """\
digraph tree {

}"""
    assert os.path.isfile('tree.dot')
    generated = read_generated_output('tree.dot')

    assert expected == generated
    os.remove('tree.dot')


def test_unicode_filename():
    tree = Tree()
    tree.create_node('Node 1', 'node_1')
    export_to_dot(tree, 'ŕʩϢ.dot')

    expected = """\
digraph tree {
\t"node_1" [label="Node 1", shape=circle]

}"""
    assert os.path.isfile('ŕʩϢ.dot')
    generated = read_generated_output('ŕʩϢ.dot')
    assert expected == generated
    os.remove('ŕʩϢ.dot')


def test_export_with_minus_in_filename():
    tree = Tree()
    tree.create_node('Example Node', 'example-node')
    expected = """\
digraph tree {
\t"example-node" [label="Example Node", shape=circle]

}"""

    export_to_dot(tree, 'id_with_minus.dot')
    assert os.path.isfile('id_with_minus.dot')
    generated = read_generated_output('id_with_minus.dot')
    assert expected == generated
    os.remove('id_with_minus.dot')
