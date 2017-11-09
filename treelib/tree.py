#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""treelib - Simple to use for you.

Python 3 Tree Implementation
"""
__author__ = 'chenxm'

import json
import copy
from collections import OrderedDict

import treelib.utils
from treelib.common import ASCIIMode, TraversalMode
from treelib.exceptions import (
    NodeNotFound, MultipleRoots, DuplicatedNode, LinkPastRootNode, LoopError
)
from .node import Node


class Tree:
    """Tree objects are made of Node(s) stored in _nodes dictionary."""

    ROOT = 0

    def __contains__(self, identifier):
        """Return a list of the nodes' identifiers matching the
        id argument.
        """
        return [node for node in self._nodes if node == identifier]

    def __init__(self, tree=None, deep=False):
        """Initiate a new tree or copy another tree with a shallow or
        deep copy.
        """

        #: dictionary, id: Node object
        self._nodes = OrderedDict()

        #: id of the root node
        self.root = None

        if tree is not None:
            self.root = tree.root

            if deep:
                for node_id in tree._nodes:
                    self._nodes[node_id] = copy.deepcopy(tree._nodes[node_id])
            else:
                self._nodes = tree._nodes

    def __getitem__(self, key) -> Node:
        """Return _nodes[key]"""
        try:
            return self._nodes[key]
        except KeyError:
            raise NodeNotFound("Node '%s' is not in the tree" % key)

    def __len__(self) -> int:
        """Return len(_nodes)"""
        return len(self._nodes)

    def __setitem__(self, key, item):
        """Set _nodes[key]"""
        self._nodes.update({key: item})

    def __str__(self) -> str:
        result = ""

        def write(line):
            nonlocal result
            result += f'{line}\n'

        treelib.utils.print_tree(self, func=write)
        return result

    @staticmethod
    def __real_true(p):
        return True

    def add_node(self, node: Node, parent: Node = None):
        """
        Add a new node to tree.
        The 'node' parameter refers to an instance of Node
        """
        if not isinstance(node, Node):
            raise TypeError('First parameter must be instance of Node.')

        if node.id in self._nodes:
            raise DuplicatedNode(f"Node with ID '{node.id}' "
                                 f"is already exists in tree.")

        pid = parent.id if isinstance(parent, Node) else parent

        if pid is None:
            if self.root is not None:
                raise MultipleRoots('A tree takes one root merely.')
            else:
                self.root = node.id
        elif not self.contains(pid):
            raise NodeNotFound(f"Parent node '{pid}' is not in the tree")

        self._nodes.update({node.id: node})
        if pid in self:
            self[pid].add_child(node.id)
        self[node.id].parent = pid

    def all_nodes(self):
        """Return all nodes in a list"""
        return list(self.all_nodes_iter())

    def all_nodes_iter(self):
        """
        Returns all nodes in an iterator
        Added by William Rusnack
        """
        return self._nodes.values()

    def children(self, nid):
        """
        Return the children (Node) list of nid.
        Empty list is returned if nid does not exist
        """
        return [self[i] for i in self.is_branch(nid)]

    def contains(self, nid):
        """Check if the tree contains node of given id"""
        return nid in self._nodes

    def create_node(self, tag=None, identifier=None, parent=None, data=None):
        """Create a child node for given @parent node."""
        node = Node(tag=tag, id=identifier, data=data)
        self.add_node(node, parent)
        return node

    def depth(self, node=None):
        """
        Get the maximum level of this tree or the level of the given node

        @param node Node instance or id
        @return int
        @throw NodeNotFound
        """
        ret = 0
        if node is None:
            # Get maximum level of this tree
            leaves = self.leaves()
            for leave in leaves:
                level = self.level(leave.id)
                ret = level if level >= ret else ret
        else:
            # Get level of the given node
            nid = node.id if isinstance(node, Node) else node
            if not self.contains(nid):
                raise NodeNotFound(f"Node '{nid}' is not in the tree")
            ret = self.level(nid)
        return ret

    def expand_tree(self, node_id=None,
                    mode: TraversalMode = TraversalMode.DEPTH,
                    filter=None, key=None, reverse: bool = False):
        """
        Python generator. Loosly based on an algorithm from
        'Essential LISP' by John R. Anderson, Albert T. Corbett, and
        Brian J. Reiser, page 239-241

        UPDATE: the @filter function is performed on Node object during
        traversing. In this manner, the traversing will not continue to
        following children of node whose condition does not pass the filter.

        UPDATE: the @key and @reverse are present to sort nodes at each
        level.
        """
        node_id = self.root if node_id is None else node_id
        if not self.contains(node_id):
            raise NodeNotFound(f"Node '{node_id}' is not in the tree")

        filter = self.__real_true if filter is None else filter

        mode = mode if isinstance(mode, TraversalMode) else TraversalMode(mode)

        if filter(self[node_id]):
            yield node_id
            queue = [self[i] for i in self[node_id].children if filter(self[i])]

            if mode in (TraversalMode.DEPTH, TraversalMode.WIDTH):
                queue.sort(key=key, reverse=reverse)
                while queue:
                    yield queue[0].id
                    expansion = [self[i] for i in queue[0].children
                                 if filter(self[i])]
                    expansion.sort(key=key, reverse=reverse)

                    if mode is TraversalMode.DEPTH:
                        queue = expansion + queue[1:]  # depth-first
                    elif mode is TraversalMode.WIDTH:
                        queue = queue[1:] + expansion  # width-first

            elif mode is TraversalMode.ZIGZAG:
                # Suggested by Ilya Kuprik (ilya-spy@ynadex.ru).
                stack_fw = []
                queue.reverse()
                stack = stack_bw = queue
                direction = False
                while stack:
                    expansion = [self[i] for i in stack[0].children
                                 if filter(self[i])]
                    yield stack.pop(0).id
                    if direction:
                        expansion.reverse()
                        stack_bw = expansion + stack_bw
                    else:
                        stack_fw = expansion + stack_fw
                    if not stack:
                        direction = not direction
                        stack = stack_fw if direction else stack_bw

    def filter_nodes(self, func):
        """Filters all nodes by function

        Function is passed one node as an argument and that node is included
        if function returns true.
        Returns a filter iterator of the node.

        Added by William Rusnack
        """
        return filter(func, self.all_nodes_iter())

    def get_node(self, nid):
        """Return the node with `nid`. None returned if `nid` does not exist."""
        if nid is None or not self.contains(nid):
            return None
        return self._nodes[nid]

    def is_branch(self, nid):
        """
        Return the children (ID) list of nid.
        Empty list is returned if nid does not exist
        """
        if nid is None:
            raise ValueError("First parameter can't be None")

        if not self.contains(nid):
            raise NodeNotFound(f"Node '{nid}' is not in the tree")

        if nid not in self:
            return []

        return self[nid].children

    def leaves(self, nid=None):
        """Get leaves of the whole tree of a subtree."""
        if nid is None:
            return [n for n in self.all_nodes_iter() if n.is_leaf]

        return [self[n] for n in self.expand_tree(nid) if self[n].is_leaf]

    def level(self, nid, filter=None):
        """
        Get the node level in this tree.
        The level is an integer starting with '0' at the root.
        In other words, the root lives at level '0';

        Update: @filter params is added to calculate level passing
        exclusive nodes.
        """
        return len([n for n in self.rsearch(nid, filter)]) - 1

    def link_past_node(self, node_id):
        """
        Delete a node by linking past it.

        For example, if we have a -> b -> c and delete node b, we are left
        with a -> c
        """
        if not self.contains(node_id):
            raise NodeNotFound(f"Node '{node_id}' is not in the tree")

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
        del self._nodes[node_id]

    def move_node(self, source, destination):
        """
        Move a node indicated by @source parameter to be a child of
        @destination.
        """
        if not self.contains(source) or not self.contains(destination):
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

    @property
    def nodes(self):
        """Return a dict form of nodes in a tree: {id: node_instance}"""
        return self._nodes

    def parent(self, node_id):
        """Get parent node object of given id"""
        if not self.contains(node_id):
            raise NodeNotFound(f"Node '{node_id}' is not in the tree")

        pid = self[node_id].parent
        if pid is None or not self.contains(pid):
            return None

        return self[pid]

    def paste(self, node_id, new_tree, deepcopy=False):
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

        if not self.contains(node_id):
            raise NodeNotFound(f"Node '{node_id}' is not in the tree")

        set_joint = set(new_tree._nodes) & set(self._nodes)  # joint keys
        if set_joint:
            # TODO: a deprecated routine is needed to avoid exception
            raise ValueError(f'Duplicated nodes {list(set_joint)} exists.')

        if deepcopy:
            for node in new_tree._nodes:
                self._nodes.update({node.id: copy.deepcopy(node)})
        else:
            self._nodes.update(new_tree._nodes)

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
        res = []

        for leaf in self.leaves():
            res.append([nid for nid in self.rsearch(leaf.id)][::-1])

        return res

    def remove_node(self, node_id):
        """
        Remove a node indicated by 'id'; all the successors are
        removed as well.

        Return the number of removed nodes.
        """
        removed = []
        if node_id is None:
            return 0

        if not self.contains(node_id):
            raise NodeNotFound(f"Node '{id}' is not in the tree")

        parent = self[node_id].parent
        for id_ in self.expand_tree(node_id):
            # TODO: implementing this function as a recursive function:
            #       check if node has children
            #       true -> run remove_node with child_id
            #       no -> delete node
            removed.append(id_)

        cnt = len(removed)

        for id_ in removed:
            del self._nodes[id_]

        # Update its parent info
        self[parent].remove_child(node_id)
        return cnt

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

        if not self.contains(node_id):
            raise NodeNotFound(f"Node '{node_id}' is not in the tree")

        subtree.root = node_id
        parent = self[node_id].parent
        self[node_id].parent = None  # reset root parent for the new tree
        removed = []

        for id_ in self.expand_tree(node_id):
            removed.append(id_)

        for id_ in removed:
            subtree._nodes.update({id_: self._nodes.pop(id_)})

        # Update its parent info
        self[parent].remove_child(node_id)
        return subtree

    def rsearch(self, node_id, filter_=None):
        """
        Traverse the tree branch along the branch from node_id to its
        ancestors (until root).
        """
        if node_id is None:
            return

        if not self.contains(node_id):
            raise NodeNotFound(f"Node '{node_id}' is not in the tree")

        filter_ = self.__real_true if filter_ is None else filter_

        current = node_id
        while current is not None:
            if filter_(self[current]):
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
            return len(self._nodes)

        if not isinstance(level, int):
            raise TypeError(f"Level should be an integer instead "
                            f"of '{type(level)}'")

        return len(
            [node for node in self.all_nodes_iter()
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

        if not self.contains(node_id):
            raise NodeNotFound(f"Node '{node_id}' is not in the tree")

        result.root = node_id
        for node_n in self.expand_tree(node_id):
            result._nodes.update({self[node_n].id: self[node_n]})

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
            queue = [self[i] for i in self[node_id].children]
            if sort:
                queue_iter = sorted(
                    queue, key=(lambda x: x) if key is None else key,
                    reverse=reverse
                )
            else:
                queue_iter = queue

            for elem in queue_iter:
                result[node_tag]['children'].append(
                    self.to_dict(elem.id, with_data=with_data,
                                 sort=sort, reverse=reverse)
                )

            if not result[node_tag]['children']:
                result = self[node_id].tag if not with_data else \
                    {node_tag: {'data': self[node_id].data}}

        return result

    def to_json(self, with_data=False, sort=True, reverse=False):
        """Return the json string corresponding to self"""
        return json.dumps(
            self.to_dict(with_data=with_data, sort=sort, reverse=reverse)
        )
