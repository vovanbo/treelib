#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""treelib - Simple to use for you.

Python 3 Tree Implementation
"""
__author__ = 'chenxm'

import json
import copy
from collections import OrderedDict
from enum import Enum

from treelib.exceptions import (
    NodeIDAbsentError, MultipleRootError, DuplicatedNodeIdError,
    LinkPastRootNodeError, LoopError
)
from .node import Node


class ASCIIMode(Enum):
    simple = ('|', '|-- ', '+-- ')
    ex = ('│', '├── ', '└── ')
    exr = ('│', '├── ', '╰── ')
    em = ('║', '╠══ ', '╚══ ')
    emv = ('║', '╟── ', '╙── ')
    emh = ('│', '╞══ ', '╘══ ')


class Tree:
    """Tree objects are made of Node(s) stored in _nodes dictionary."""

    #: ROOT, DEPTH, WIDTH, ZIGZAG constants :
    (ROOT, DEPTH, WIDTH, ZIGZAG) = list(range(4))

    def __contains__(self, identifier):
        """Return a list of the nodes' identifiers matching the
        identifier argument.
        """
        return [node for node in self._nodes if node == identifier]

    def __init__(self, tree=None, deep=False):
        """Initiate a new tree or copy another tree with a shallow or
        deep copy.
        """

        #: dictionary, identifier: Node object
        self._nodes = OrderedDict()

        #: identifier of the root node
        self.root = None

        if tree is not None:
            self.root = tree.root

            if deep:
                for nid in tree._nodes:
                    self._nodes[nid] = copy.deepcopy(tree._nodes[nid])
            else:
                self._nodes = tree._nodes

    def __getitem__(self, key):
        """Return _nodes[key]"""
        try:
            return self._nodes[key]
        except KeyError:
            raise NodeIDAbsentError("Node '%s' is not in the tree" % key)

    def __len__(self):
        """Return len(_nodes)"""
        return len(self._nodes)

    def __setitem__(self, key, item):
        """Set _nodes[key]"""
        self._nodes.update({key: item})

    def __str__(self):
        result = ""

        def write(line):
            nonlocal result
            result += f'{line}\n'

        self.__print_backend(func=write)
        return result

    @staticmethod
    def __get_label(node, data_property, id_hidden):
        result = getattr(node.data, data_property) \
            if data_property \
            else node.tag

        return result if id_hidden else f'{result}[{node.identifier}]'

    def __print_backend(self, nid=None, level=ROOT, id_hidden=True, filter=None,
                        key=None, reverse=False, ascii_mode=ASCIIMode.ex,
                        data_property=None, func=print):
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

        # iter with func
        for pre, node in self.__get(nid, level, filter, key_func, reverse,
                                    ascii_mode):
            label = self.__get_label(node, data_property, id_hidden)
            func('{0}{1}'.format(pre, label))

    def __get(self, nid, level, filter_, key, reverse, ascii_mode):
        filter_ = (lambda x: True) if filter_ is None else filter_

        # render characters
        dt = ascii_mode.value \
            if isinstance(ascii_mode, ASCIIMode) \
            else ASCIIMode[ascii_mode].value

        return self.__get_iter(nid, level, filter_, key, reverse, dt, [])

    def __get_iter(self, nid, level, filter_, key, reverse, dt, is_last):
        dt_vline, dt_line_box, dt_line_cor = dt

        nid = self.root if (nid is None) else nid
        if not self.contains(nid):
            raise NodeIDAbsentError(f"Node '{nid}' is not in the tree")

        node = self[nid]

        if level == self.ROOT:
            yield "", node
        else:
            leading = ''.join(dt_vline + ' ' * 3 if not x else ' ' * 4
                              for x in is_last[0:-1])
            lasting = dt_line_cor if is_last[-1] else dt_line_box
            yield leading + lasting, node

        if filter_(node) and node.expanded:
            children = [self[i] for i in node.fpointer if filter_(self[i])]
            idxlast = len(children) - 1

            if key:
                children_iter = sorted(children, key=key, reverse=reverse)
            elif reverse:
                children_iter = reversed(children)
            else:
                children_iter = children

            level += 1
            for idx, child in enumerate(children_iter):
                is_last.append(idx == idxlast)
                for item in self.__get_iter(child.identifier, level, filter_,
                                            key, reverse, dt, is_last):
                    yield item
                is_last.pop()

    def __update_bpointer(self, nid, parent_id):
        """set self[nid].bpointer"""
        self[nid].update_bpointer(parent_id)

    def __update_fpointer(self, nid, child_id, mode):
        if nid is None:
            return
        else:
            self[nid].update_fpointer(child_id, mode)

    @staticmethod
    def __real_true(p):
        return True

    def add_node(self, node, parent=None):
        """
        Add a new node to tree.
        The 'node' parameter refers to an instance of Class::Node
        """
        if not isinstance(node, Node):
            raise TypeError('First parameter must be instance of Node.')

        if node.identifier in self._nodes:
            raise DuplicatedNodeIdError(f"Can't create node "
                                        f"with ID '{node.identifier}'")

        pid = parent.identifier if isinstance(parent, Node) else parent

        if pid is None:
            if self.root is not None:
                raise MultipleRootError('A tree takes one root merely.')
            else:
                self.root = node.identifier
        elif not self.contains(pid):
            raise NodeIDAbsentError(f"Parent node '{pid}' is not in the tree")

        self._nodes.update({node.identifier: node})
        self.__update_fpointer(pid, node.identifier, Node.ADD)
        self.__update_bpointer(node.identifier, pid)

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
        node = Node(tag=tag, identifier=identifier, data=data)
        self.add_node(node, parent)
        return node

    def depth(self, node=None):
        """
        Get the maximum level of this tree or the level of the given node

        @param node Node instance or identifier
        @return int
        @throw NodeIDAbsentError
        """
        ret = 0
        if node is None:
            # Get maximum level of this tree
            leaves = self.leaves()
            for leave in leaves:
                level = self.level(leave.identifier)
                ret = level if level >= ret else ret
        else:
            # Get level of the given node
            nid = node.identifier if isinstance(node, Node) else node
            if not self.contains(nid):
                raise NodeIDAbsentError(f"Node '{nid}' is not in the tree")
            ret = self.level(nid)
        return ret

    def expand_tree(self, nid=None, mode=DEPTH, filter=None, key=None,
                    reverse=False):
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
        nid = self.root if (nid is None) else nid
        if not self.contains(nid):
            raise NodeIDAbsentError(f"Node '{nid}' is not in the tree")

        filter = self.__real_true if (filter is None) else filter
        if filter(self[nid]):
            yield nid
            queue = [self[i] for i in self[nid].fpointer if filter(self[i])]
            if mode in [self.DEPTH, self.WIDTH]:
                queue.sort(key=key, reverse=reverse)
                while queue:
                    yield queue[0].identifier
                    expansion = [self[i] for i in queue[0].fpointer
                                 if filter(self[i])]
                    expansion.sort(key=key, reverse=reverse)
                    if mode is self.DEPTH:
                        queue = expansion + queue[1:]  # depth-first
                    elif mode is self.WIDTH:
                        queue = queue[1:] + expansion  # width-first

            elif mode is self.ZIGZAG:
                # Suggested by Ilya Kuprik (ilya-spy@ynadex.ru).
                stack_fw = []
                queue.reverse()
                stack = stack_bw = queue
                direction = False
                while stack:
                    expansion = [self[i] for i in stack[0].fpointer
                                 if filter(self[i])]
                    yield stack.pop(0).identifier
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
            raise NodeIDAbsentError(f"Node '{nid}' is not in the tree")

        if nid not in self:
            return []

        return self[nid].fpointer

    def leaves(self, nid=None):
        """Get leaves of the whole tree of a subtree."""
        leaves = []
        if nid is None:
            for node in self.all_nodes_iter():
                if node.is_leaf:
                    leaves.append(node)
        else:
            for node in self.expand_tree(nid):
                if self[node].is_leaf:
                    leaves.append(self[node])
        return leaves

    def level(self, nid, filter=None):
        """
        Get the node level in this tree.
        The level is an integer starting with '0' at the root.
        In other words, the root lives at level '0';

        Update: @filter params is added to calculate level passing
        exclusive nodes.
        """
        return len([n for n in self.rsearch(nid, filter)]) - 1

    def link_past_node(self, nid):
        """
        Delete a node by linking past it.

        For example, if we have a -> b -> c and delete node b, we are left
        with a -> c
        """
        if not self.contains(nid):
            raise NodeIDAbsentError(f"Node '{nid}' is not in the tree")

        if self.root == nid:
            raise LinkPastRootNodeError('Cannot link past the root node, '
                                        'delete it with remove_node()')

        # Get the parent of the node we are linking past
        parent = self[self[nid].bpointer]

        # Set the children of the node to the parent
        for child in self[nid].fpointer:
            self[child].update_bpointer(parent.identifier)

        # Link the children to the parent
        parent.fpointer += self[nid].fpointer
        # Delete the node
        parent.update_fpointer(nid, mode=parent.DELETE)
        del self._nodes[nid]

    def move_node(self, source, destination):
        """
        Move a node indicated by @source parameter to be a child of
        @destination.
        """
        if not self.contains(source) or not self.contains(destination):
            raise NodeIDAbsentError
        elif self.is_ancestor(source, destination):
            raise LoopError

        parent = self[source].bpointer
        self.__update_fpointer(parent, source, Node.DELETE)
        self.__update_fpointer(destination, source, Node.ADD)
        self.__update_bpointer(source, destination)

    def is_ancestor(self, ancestor, grandchild):
        parent = self[grandchild].bpointer
        child = grandchild

        while parent is not None:
            if parent == ancestor:
                return True

            child = self[child].bpointer
            parent = self[child].bpointer

        return False

    @property
    def nodes(self):
        """Return a dict form of nodes in a tree: {id: node_instance}"""
        return self._nodes

    def parent(self, nid):
        """Get parent node object of given id"""
        if not self.contains(nid):
            raise NodeIDAbsentError(f"Node '{nid}' is not in the tree")

        pid = self[nid].bpointer
        if pid is None or not self.contains(pid):
            return None

        return self[pid]

    def paste(self, nid, new_tree, deepcopy=False):
        """
        Paste a @new_tree to the original one by linking the root
        of new tree to given node (nid).

        Update: add @deepcopy of pasted tree.
        """
        if not isinstance(new_tree, Tree):
            raise TypeError('Instance of Tree is required as '
                            '"new_tree" parameter.')

        if nid is None:
            raise ValueError('First parameter can not be None')

        if not self.contains(nid):
            raise NodeIDAbsentError(f"Node '{nid}' is not in the tree")

        set_joint = set(new_tree._nodes) & set(self._nodes)  # joint keys
        if set_joint:
            # TODO: a deprecated routine is needed to avoid exception
            raise ValueError(f'Duplicated nodes {list(set_joint)} exists.')

        if deepcopy:
            for node in new_tree._nodes:
                self._nodes.update({node.identifier: copy.deepcopy(node)})
        else:
            self._nodes.update(new_tree._nodes)
        self.__update_fpointer(nid, new_tree.root, Node.ADD)
        self.__update_bpointer(new_tree.root, nid)

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
            res.append([nid for nid in self.rsearch(leaf.identifier)][::-1])

        return res

    def remove_node(self, identifier):
        """
        Remove a node indicated by 'identifier'; all the successors are
        removed as well.

        Return the number of removed nodes.
        """
        removed = []
        if identifier is None:
            return 0

        if not self.contains(identifier):
            raise NodeIDAbsentError(f"Node '{identifier}' is not in the tree")

        parent = self[identifier].bpointer
        for id_ in self.expand_tree(identifier):
            # TODO: implementing this function as a recursive function:
            #       check if node has children
            #       true -> run remove_node with child_id
            #       no -> delete node
            removed.append(id_)

        cnt = len(removed)

        for id_ in removed:
            del self._nodes[id_]

        # Update its parent info
        self.__update_fpointer(parent, identifier, Node.DELETE)

        return cnt

    def remove_subtree(self, nid):
        """
        Return a subtree deleted from this tree. If nid is None, an
        empty tree is returned.
        For the original tree, this method is similar to
        `remove_node(self,nid)`, because given node and its children
        are removed from the original tree in both methods.
        For the returned value and performance, these two methods are
        different:

            `remove_node` returns the number of deleted nodes;
            `remove_subtree` returns a subtree of deleted nodes;

        You are always suggested to use `remove_node` if your only to
        delete nodes from a tree, as the other one need memory
        allocation to store the new tree.
        """
        st = Tree()
        if nid is None:
            return st

        if not self.contains(nid):
            raise NodeIDAbsentError(f"Node '{nid}' is not in the tree")

        st.root = nid
        parent = self[nid].bpointer
        self[nid].bpointer = None  # reset root parent for the new tree
        removed = []

        for id_ in self.expand_tree(nid):
            removed.append(id_)

        for id_ in removed:
            st._nodes.update({id_: self._nodes.pop(id_)})

        # Update its parent info
        self.__update_fpointer(parent, nid, Node.DELETE)
        return st

    def rsearch(self, nid, filter_=None):
        """
        Traverse the tree branch along the branch from nid to its
        ancestors (until root).
        """
        if nid is None:
            return

        if not self.contains(nid):
            raise NodeIDAbsentError(f"Node '{nid}' is not in the tree")

        filter_ = self.__real_true if filter_ is None else filter_

        current = nid
        while current is not None:
            if filter_(self[current]):
                yield current
            # subtree() hasn't update the bpointer
            current = self[current].bpointer if self.root != current else None

    def save2file(self, filename, nid=None, level=ROOT, id_hidden=True,
                  filter_=None, key=None, reverse=False,
                  ascii_mode=ASCIIMode.ex, data_property=None):
        """Update 20/05/13: Save tree into file for offline analysis"""

        def _write_line(line, f):
            f.write(line + b'\n')

        self.__print_backend(
            nid, level, id_hidden, filter_, key, reverse, ascii_mode,
            data_property, func=lambda x: _write_line(x, open(filename, 'ab'))
        )

    def show(self, nid=None, level=ROOT, id_hidden=True, filter_=None,
             key=None, reverse=False, ascii_mode=ASCIIMode.ex,
             data_property=None):
        result = ""

        def write(line):
            nonlocal result
            result += f'{line}\n'

        try:
            self.__print_backend(nid, level, id_hidden, filter_,
                                 key, reverse, ascii_mode, data_property,
                                 func=write)
        except NodeIDAbsentError:
            print('Tree is empty')

        print(result)

    def siblings(self, nid):
        """
        Return the siblings of given @nid.

        If @nid is root or there are no siblings, an empty list is returned.
        """
        siblings = []

        if nid != self.root:
            pid = self[nid].bpointer
            siblings = [self[i] for i in self[pid].fpointer if i != nid]

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
             if self.level(node.identifier) == level]
        )

    def subtree(self, nid):
        """
        Return a shallow COPY of subtree with nid being the new root.
        If nid is None, return an empty tree.
        If you are looking for a deepcopy, please create a new tree
        with this shallow copy,

        e.g.
            new_tree = Tree(t.subtree(t.root), deep=True)

        This line creates a deep copy of the entire tree.
        """
        result = Tree()
        if nid is None:
            return result

        if not self.contains(nid):
            raise NodeIDAbsentError(f"Node '{nid}' is not in the tree")

        result.root = nid
        for node_n in self.expand_tree(nid):
            result._nodes.update({self[node_n].identifier: self[node_n]})

        return result

    def to_dict(self, nid=None, key=None, sort=True, reverse=False,
                with_data=False):
        """transform self into a dict"""

        nid = self.root if (nid is None) else nid
        ntag = self[nid].tag
        result = {ntag: {'children': []}}
        if with_data:
            result[ntag]['data'] = self[nid].data

        if self[nid].expanded:
            queue = [self[i] for i in self[nid].fpointer]
            if sort:
                queue_iter = sorted(
                    queue, key=(lambda x: x) if key is None else key,
                    reverse=reverse
                )
            else:
                queue_iter = queue

            for elem in queue_iter:
                result[ntag]['children'].append(
                    self.to_dict(elem.identifier, with_data=with_data,
                                 sort=sort, reverse=reverse)
                )

            if not result[ntag]['children']:
                result = self[nid].tag if not with_data else \
                    {ntag: {'data': self[nid].data}}

        return result

    def to_json(self, with_data=False, sort=True, reverse=False):
        """Return the json string corresponding to self"""
        return json.dumps(
            self.to_dict(with_data=with_data, sort=sort, reverse=reverse)
        )
