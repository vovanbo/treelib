#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""treelib - Simple to use for you.

Python 3 Tree Implementation
"""
__author__ = 'chenxm'

import json
import copy
from collections import OrderedDict
from typing import Callable

import treelib.utils
from treelib.common import ASCIIMode, TraversalMode
from treelib.exceptions import (
    NodeNotFound, MultipleRoots, DuplicatedNode, LinkPastRootNode, LoopError
)
from .node import Node


class Tree(OrderedDict):
    """Tree objects are made of Node(s) stored in _nodes dictionary."""
    def __init__(self, tree: 'Tree' = None, deepcopy: bool = False):
        """Initiate a new tree or copy another tree with a shallow or
        deepcopy copy.
        """
        super(Tree, self).__init__()

        #: id of the root node
        self.root = None

        if tree is not None:
            if not isinstance(tree, Tree):
                raise TypeError('Tree instance is required.')

            self.root = tree.root
            self.__merge_tree(tree, deepcopy)

    def __str__(self) -> str:
        return treelib.utils.print_tree(self, ascii_mode='simple')

    def __getitem__(self, item):
        try:
            return super(Tree, self).__getitem__(item)
        except KeyError:
            raise NodeNotFound(f"Node '{item}' is not in the tree")

    def __merge_tree(self, other: 'Tree', deepcopy: bool = False):
        if deepcopy:
            for node_id in other:
                self[node_id] = copy.deepcopy(other[node_id])
        else:
            self.update(other)

    def add_node(self, node: Node, parent: Node = None):
        """
        Add a new node to tree.
        The 'node' parameter refers to an instance of Node
        """
        if not isinstance(node, Node):
            raise TypeError('First parameter must be instance of Node.')

        if node.id in self:
            raise DuplicatedNode(f"Node with ID '{node.id}' "
                                 f"is already exists in tree.")

        pid = parent.id if isinstance(parent, Node) else parent

        if pid is None:
            if self.root is not None:
                raise MultipleRoots('A tree takes one root merely.')
            else:
                self.root = node.id
        elif pid not in self:
            raise NodeNotFound(f"Parent node '{pid}' is not in the tree")

        self[node.id] = node
        if pid in self:
            self[pid].add_child(node.id)
        self[node.id].parent = pid

    def children(self, node_id):
        """
        Return the children (Node) list of node_id.
        Empty list is returned if node_id does not exist
        """
        return [self[i] for i in self.is_branch(node_id)]

    def create_node(self, *args, parent=None, node_cls=Node, **kwargs):
        """Create a child node for given @parent node."""
        if not issubclass(node_cls, Node):
            raise ValueError('node_cls must be a subclass of Node.')

        node = node_cls(*args, **kwargs)
        self.add_node(node, parent)
        return node

    def depth(self, node=None):
        """
        Get the maximum level of this tree or the level of the given node

        @param node Node instance or id
        @return int
        @throw NodeNotFound
        """
        result = 0
        if node is None:
            # Get maximum level of this tree
            for leaf in self.leaves():
                level = self.level(leaf.id)
                result = level if level >= result else result
        else:
            # Get level of the given node
            node_id = node.id if isinstance(node, Node) else node

            if node_id not in self:
                raise NodeNotFound(f"Node '{node_id}' is not in the tree")

            result = self.level(node_id)
        return result

    def expand_tree(self, node_id=None,
                    mode: TraversalMode = TraversalMode.DEPTH,
                    filtering: Callable[[Node], bool] = None,
                    key=None, reverse: bool = False):
        """
        Python generator. Loosly based on an algorithm from
        'Essential LISP' by John R. Anderson, Albert T. Corbett, and
        Brian J. Reiser, page 239-241

        UPDATE: the @filtering function is performed on Node object during
        traversing. In this manner, the traversing will not continue to
        following children of node whose condition does not pass the filter.

        UPDATE: the @key and @reverse are present to sort nodes at each
        level.
        """
        node_id = self.root if node_id is None else node_id

        if node_id not in self:
            raise NodeNotFound(f"Node '{node_id}' is not in the tree")

        if filtering is not None and not callable(filtering):
            raise TypeError('Filtering must be callable.')

        mode = mode if isinstance(mode, TraversalMode) else TraversalMode(mode)

        if filtering is not None and not filtering(self[node_id]):
            return

        yield node_id
        queue = (self[i] for i in self[node_id].children)

        if filtering is not None:
            queue = filter(filtering, queue)

        if mode in (TraversalMode.DEPTH, TraversalMode.WIDTH):
            queue = sorted(queue, key=key, reverse=reverse)
            while queue:
                yield queue[0].id
                expansion = sorted(
                    filter(filtering, (self[i] for i in queue[0].children)),
                    key=key, reverse=reverse
                )

                if mode is TraversalMode.DEPTH:
                    queue = expansion + queue[1:]  # depth-first
                elif mode is TraversalMode.WIDTH:
                    queue = queue[1:] + expansion  # width-first

        elif mode is TraversalMode.ZIGZAG:
            # Suggested by Ilya Kuprik (ilya-spy@ynadex.ru).
            stack_fw = []
            queue = list(queue)
            queue.reverse()
            stack = stack_bw = queue
            direction = False
            while stack:
                expansion = filter(filtering,
                                   (self[i] for i in stack[0].children))
                yield stack.pop(0).id
                expansion = list(expansion)
                if direction:
                    expansion.reverse()
                    stack_bw = expansion + stack_bw
                else:
                    stack_fw = expansion + stack_fw
                if not stack:
                    direction = not direction
                    stack = stack_fw if direction else stack_bw

    def is_branch(self, node_id):
        """
        Return the children (ID) list of node_id.
        Empty list is returned if node_id does not exist
        """
        if node_id is None:
            raise ValueError("First parameter can't be None")

        return self[node_id].children

    def leaves(self, node_id=None):
        """Get leaves of the whole tree of a subtree."""
        if node_id is None:
            return [n for n in self.values() if n.is_leaf]

        return [self[n] for n in self.expand_tree(node_id) if self[n].is_leaf]

    def level(self, node_id, filtering: Callable[[Node], bool] = None):
        """
        Get the node level in this tree.
        The level is an integer starting with '0' at the root.
        In other words, the root lives at level '0';

        Update: @filtering params is added to calculate level passing
        exclusive nodes.
        """
        return len([n for n in self.rsearch(node_id, filtering)]) - 1

    def link_past_node(self, node_id):
        """
        Delete a node by linking past it.

        For example, if we have a -> b -> c and delete node b, we are left
        with a -> c
        """
        if self.root == node_id:
            raise LinkPastRootNode('Cannot link past the root node, '
                                   'delete it with remove_node()')

        # Get the parent of the node we are linking past
        parent = self[self[node_id].parent]

        # Set the children of the node to the parent
        for child in self[node_id].children:
            self[child].parent = parent.id

        # Link the children to the parent
        parent.children += self[node_id].children
        # Delete the node
        parent.remove_child(node_id)
        del self[node_id]

    def move_node(self, source, destination):
        """
        Move a node indicated by @source parameter to be a child of
        @destination.
        """
        if source not in self or destination not in self:
            raise NodeNotFound

        if self.is_ancestor(source, destination):
            raise LoopError

        parent = self[source].parent
        self[parent].remove_child(source)
        self[destination].add_child(source)
        self[source].parent = destination

    def is_ancestor(self, ancestor, grandchild):
        parent = self[grandchild].parent
        child = grandchild

        while parent is not None:
            if parent == ancestor:
                return True

            child = self[child].parent
            parent = self[child].parent

        return False

    def parent(self, node_id):
        """Get parent node object of given id"""
        pid = self[node_id].parent
        if pid is None or pid not in self:
            return None

        return self[pid]

    def paste(self, node_id, new_tree: 'Tree', deepcopy: bool = False):
        """
        Paste a @new_tree to the original one by linking the root
        of new tree to given node (node_id).

        Update: add @deepcopy of pasted tree.
        """
        if not isinstance(new_tree, Tree):
            raise TypeError('Instance of Tree is required as '
                            '"new_tree" parameter.')

        if node_id is None:
            raise ValueError('First parameter can not be None')

        if node_id not in self:
            raise NodeNotFound(f"Node '{node_id}' is not in the tree")

        set_joint = set(new_tree) & set(self)  # joint keys
        if set_joint:
            # TODO: a deprecated routine is needed to avoid exception
            raise ValueError(f'Duplicated nodes {list(set_joint)} exists.')

        self.__merge_tree(new_tree, deepcopy)

        self[node_id].add_child(new_tree.root)
        self[new_tree.root].parent = node_id

    def paths_to_leaves(self):
        """
        Use this function to get the identifiers allowing to go from the root
        nodes to each leaf.
        Return a list of list of identifiers, root being not omitted.

        For example :
            Harry
            |___ Bill
            |___ Jane
            |    |___ Diane
            |         |___ George
            |              |___ Jill
            |         |___ Mary
            |    |___ Mark

        expected result :
        [['harry', 'jane', 'diane', 'mary'],
         ['harry', 'jane', 'mark'],
         ['harry', 'jane', 'diane', 'george', 'jill'],
         ['harry', 'bill']]
        """
        return [
            [nid for nid in self.rsearch(l.id)][::-1]
            for l in self.leaves()
        ]

    def remove_node(self, node_id):
        """
        Remove a node indicated by 'id'; all the successors are
        removed as well.

        Return the number of removed nodes.
        """
        if node_id is None:
            return 0

        parent = self[node_id].parent

        removed = [n for n in self.expand_tree(node_id)]
        for id_ in removed:
            del self[id_]

        # Update its parent info
        self[parent].remove_child(node_id)
        return len(removed)

    def remove_subtree(self, node_id):
        """
        Return a subtree deleted from this tree. If node_id is None, an
        empty tree is returned.
        For the original tree, this method is similar to
        `remove_node(self,node_id)`, because given node and its children
        are removed from the original tree in both methods.
        For the returned value and performance, these two methods are
        different:

            `remove_node` returns the number of deleted nodes;
            `remove_subtree` returns a subtree of deleted nodes;

        You are always suggested to use `remove_node` if your only to
        delete nodes from a tree, as the other one need memory
        allocation to store the new tree.
        """
        subtree = Tree()
        if node_id is None:
            return subtree

        subtree.root = node_id
        parent = self[node_id].parent
        self[node_id].parent = None  # reset root parent for the new tree

        removed = [n for n in self.expand_tree(node_id)]
        for id_ in removed:
            subtree[id_] = self.pop(id_)

        # Update its parent info
        self[parent].remove_child(node_id)
        return subtree

    def rsearch(self, node_id, filtering: Callable[[Node], bool] = None):
        """
        Traverse the tree branch along the branch from node_id to its
        ancestors (until root).
        """
        if node_id is None:
            return

        if node_id not in self:
            raise NodeNotFound(f"Node '{node_id}' is not in the tree")

        if filtering is not None and not callable(filtering):
            raise TypeError('Filtering must be a callable.')

        current = node_id
        while current is not None:
            if filtering is None or filtering(self[current]):
                yield current

            # subtree() hasn't update the parent
            current = self[current].parent if self.root != current else None

    def save2file(self, filename, node_id=None, id_hidden=True,
                  filter_=None, key=None, reverse=False,
                  ascii_mode=ASCIIMode.ex, data_property=None):
        """Update 20/05/13: Save tree into file for offline analysis"""
        with open(filename, 'ab') as fp:
            treelib.utils.print_tree(
                self, node_id, id_hidden, filter_, key, reverse,
                ascii_mode, data_property, func=lambda n: fp.write(n + b'\n')
            )

    def print(self, node_id=None, id_hidden=True, filter_=None,
              key=None, reverse=False, ascii_mode=ASCIIMode.ex,
              data_property=None):
        try:
            treelib.utils.print_tree(
                self, node_id, id_hidden, filter_,
                key, reverse, ascii_mode, data_property,
                func=print
            )
        except NodeNotFound:
            print('Tree is empty')

    def siblings(self, node_id):
        """
        Return the siblings of given @node_id.

        If @node_id is root or there are no siblings, an empty list is returned.
        """
        siblings = []

        if node_id != self.root:
            pid = self[node_id].parent
            siblings = [self[c] for c in self[pid].children if c != node_id]

        return siblings

    def size(self, level: int = None):
        """
        Get the number of nodes of the whole tree if @level is not
        given. Otherwise, the total number of nodes at specific level
        is returned.

        @param level The level number in the tree. It must be between
        [0, tree.depth].

        Otherwise, InvalidLevelNumber exception will be raised.
        """
        if level is None:
            return len(self)

        if not isinstance(level, int):
            raise TypeError(f"Level should be an integer instead "
                            f"of '{type(level)}'")

        return len(
            [node for node in self.values()
             if self.level(node.id) == level]
        )

    def subtree(self, node_id):
        """
        Return a shallow COPY of subtree with node_id being the new root.
        If node_id is None, return an empty tree.
        If you are looking for a deepcopy, please create a new tree
        with this shallow copy,

        e.g.
            new_tree = Tree(t.subtree(t.root), deep=True)

        This line creates a deep copy of the entire tree.
        """
        result = Tree()
        if node_id is None:
            return result

        if node_id not in self:
            raise NodeNotFound(f"Node '{node_id}' is not in the tree")

        result.root = node_id
        for subtree_node in self.expand_tree(node_id):
            result[self[subtree_node].id] = self[subtree_node]

        return result

    def to_dict(self, node_id=None, key=None, sort=True, reverse=False,
                with_data=False):
        """transform self into a dict"""

        node_id = self.root if node_id is None else node_id
        node_tag = self[node_id].tag
        result = {node_tag: {'children': []}}
        if with_data:
            result[node_tag]['data'] = self[node_id].data

        if self[node_id].expanded:
            queue = (self[i] for i in self[node_id].children)
            if sort:
                queue = sorted(
                    queue, key=(lambda x: x) if key is None else key,
                    reverse=reverse
                )

            for elem in queue:
                result[node_tag]['children'].append(
                    self.to_dict(elem.id, with_data=with_data, sort=sort,
                                 reverse=reverse)
                )

            if not result[node_tag]['children']:
                result = (
                    self[node_id].tag
                    if not with_data
                    else {node_tag: {'data': self[node_id].data}}
                )

        return result

    def to_json(self, with_data=False, sort=True, reverse=False):
        """Return the json string corresponding to self"""
        return json.dumps(
            self.to_dict(with_data=with_data, sort=sort, reverse=reverse)
        )
