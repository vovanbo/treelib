#!/usr/bin/env python

"""
Example of ttree usage to generate recursive tree of directories.
It could be useful to implement Directory Tree data structure

2016 samuelsh
"""

import ttree
import random
from hashlib import blake2b
from string import digits, ascii_letters

MAX_FILES_PER_DIR = 10


def get_random_string(length):
    return ''.join(random.choice(digits + ascii_letters) for _ in range(length))


def build_recursive_tree(tree, base, depth, width):
    """
    Args:
        tree: Tree
        base: Node
        depth: int
        width: int

    Returns:

    """
    while depth >= 0:
        depth -= 1
        for _ in range(width):
            directory = Directory()
            tree.create_node(
                directory.name,
                # node id is md5 hash of it's name
                blake2b(directory.name.encode()).hexdigest(),
                parent=base.id,
                data=directory
            )
        dirs_nodes = tree.children(base.id)
        for dir in dirs_nodes:
            newbase = tree.get(dir.id)
            build_recursive_tree(tree, newbase, depth, width)


class Directory:
    def __init__(self):
        self._name = get_random_string(64)
        # Each directory contains 1000 files
        self._files = [File() for _ in range(MAX_FILES_PER_DIR)]

    @property
    def name(self):
        return self._name

    @property
    def files(self):
        return self._files


class File:
    def __init__(self):
        self._name = get_random_string(64)

    @property
    def name(self):
        return self._name


tree = ttree.Tree()
base = tree.create_node('Root', 'root')
build_recursive_tree(tree, base, 2, 10)

tree.print()
