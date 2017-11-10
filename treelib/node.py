#!/usr/bin/env python
"""treelib - Simple to use for you.
   Python 3 Tree Implementation
"""

import uuid

from collections import Sequence, MutableMapping, Set


class Node:
    """
    Nodes are elementary objects which are stored a `_nodes` dictionary
    of a Tree.
    Use `data` attribute to store node-specific data.
    """
    def __init__(self, tag=None, id=None, expanded=True, data=None):
        """Create a new Node object to be placed inside a Tree object"""

        #: if given as a parameter, must be unique
        self._id = None
        self._set_id(id)

        #: None or something else
        #: if None, self._id will be set to the id's value.
        self._tag = self._id if tag is None else tag

        #: boolean
        self.expanded = expanded

        #: id of the parent's node :
        self._parent = None
        #: id(s) of the soons' node(s) :
        self._children = list()

        #: None or whatever given as a parameter
        self.data = data

    def __repr__(self):
        kwargs = (f"tag={self.tag!r}",
                  f"id={self.id!r}",
                  f"data={self.data!r}")
        return f"{self.__class__.__name__}({', '.join(kwargs)})"

    def __lt__(self, other):
        return self.tag < other.tag

    def _set_id(self, node_id):
        """Initialize self._set_id"""
        self._id = uuid.uuid1() if node_id is None else node_id

    @property
    def parent(self):
        """Return the value of `_parent`."""
        return self._parent

    @parent.setter
    def parent(self, node_id):
        """Set the value of `_parent`."""
        self._parent = node_id

    @property
    def children(self):
        """Return the value of `_children`."""
        return self._children

    @children.setter
    def children(self, value):
        """Set the value of `_children`."""
        if value is None:
            self._children = list()
        elif isinstance(value, (Sequence, Set)):
            self._children = list(value)
        elif isinstance(value, MutableMapping):
            self._children = list(value.keys())
        else:
            raise ValueError('Sequence, Set or MutableMapping '
                             'are allowed values for children only.')

    @property
    def id(self):
        """Return the value of `_id`."""
        return self._id

    @id.setter
    def id(self, value):
        """Set the value of `_id`."""
        if value is None:
            raise ValueError("Node ID can not be None")

        self._set_id(value)

    @property
    def is_leaf(self):
        """Return true if current node has no children."""
        return not self.children

    @property
    def is_root(self):
        """Return true if self has no parent, i.e. as root."""
        return self._parent is None

    @property
    def tag(self):
        """Return the value of `_tag`."""
        return self._tag

    @tag.setter
    def tag(self, value):
        """Set the value of `_tag`."""
        self._tag = value

    def add_child(self, node_id):
        if node_id is not None:
            self._children.append(node_id)

    def remove_child(self, node_id):
        if node_id is not None and node_id in self._children:
            self._children.remove(node_id)
