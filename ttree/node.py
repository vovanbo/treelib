#!/usr/bin/env python
import uuid

from collections import Sequence, MutableMapping, Set


class Node:
    """
    Represent a tree node.

    A :class:`Node` object contains basic properties such as node id,
    node tag, parent node, children nodes etc., and some operations for a node.

    Nodes are elementary objects which are stored in a dictionary
    of a Tree. Use `data` attribute to store node-specific data.
    """
    def __init__(self, tag=None, id=None, expanded=True, data=None, tree=None):
        """Create a new Node object to be placed inside a Tree object"""

        #: if given as a parameter, must be unique
        self._id = None
        self._set_id(id)

        #: None or something else
        #: if None, self._id will be set to the id's value.
        self._tag = self._id if tag is None else tag

        #: boolean
        self.expanded = expanded

        #: id of the parent's node
        self._parent = None
        #: id(s) of the children node(s)
        self._children = list()

        self._tree = tree
        #: User payload associated with this node.
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
    def id(self):
        """
        Return the value of `_id`.

        The unique ID of a node within the scope of a tree. This attribute
        can be accessed and modified with ``.`` and ``=`` operator
        respectively.
        """
        return self._id

    @id.setter
    def id(self, value):
        """Set the value of `_id`."""
        if value is None:
            raise ValueError("Node ID can not be None")

        self._set_id(value)

    @property
    def tag(self):
        """
        Return the value of `_tag`.

        The readable node name for human. This attribute can be accessed and
        modified with ``.`` and ``=`` operator respectively.
        """
        return self._tag

    @tag.setter
    def tag(self, value):
        """Set the value of `_tag`."""
        self._tag = value

    @property
    def parent(self):
        """
        Return the value of `_parent`.

        The parent ID of a node. This attribute can be accessed and modified
        with ``.`` and ``=`` operator respectively.
        """
        return self._parent

    @parent.setter
    def parent(self, node_id):
        """Set the value of `_parent`."""
        self._parent = node_id

    @property
    def children(self):
        """
        Return the value of `_children`.

        With a getting operator, a list of IDs of node's children is obtained.
        With a setting operator, the value can be list, set, or dict.
        For list or set, it is converted to a list type by the package;
        for dict, the keys are treated as the node IDs.
        """
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
    def is_leaf(self):
        """
        Check if the node has children.

        Return False if the ``children`` is empty or None.
        """
        return not self.children

    @property
    def is_root(self):
        """Check if the node is the root of present tree."""
        return self._parent is None

    @property
    def tree(self):
        """Return tree instance of node."""
        return self._tree

    def add_child(self, node_id):
        """Add child (indicated by the ``node_id`` parameter) of a node."""
        if node_id is not None:
            self._children.append(node_id)

    def remove_child(self, node_id):
        """Remove child (indicated by the ``node_id`` parameter) of a node."""
        if node_id is not None and node_id in self._children:
            self._children.remove(node_id)
