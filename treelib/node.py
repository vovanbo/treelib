#!/usr/bin/env python
"""treelib - Simple to use for you.
   Python 3 Tree Implementation
"""

import uuid

import warnings
from collections import Sequence, MutableMapping, Set


class Node:
    """
    Nodes are elementary objects which are stored a `_nodes` dictionary of a Tree.
    Use `data` attribute to store node-specific data.
    """

    #: ADD, DELETE, INSERT constants :
    (ADD, DELETE) = list(range(2))

    def __init__(self, tag=None, identifier=None, expanded=True, data=None):
        """Create a new Node object to be placed inside a Tree object"""

        #: if given as a parameter, must be unique
        self._identifier = None
        self._set_identifier(identifier)

        #: None or something else
        #: if None, self._identifier will be set to the identifier's value.
        if tag is None:
            self._tag = self._identifier
        else:
            self._tag = tag

        #: boolean
        self.expanded = expanded

        #: identifier of the parent's node :
        self._bpointer = None
        #: identifier(s) of the soons' node(s) :
        self._fpointer = list()

        #: None or whatever given as a parameter
        self.data = data

    def __repr__(self):
        name = self.__class__.__name__
        kwargs = (
            f"tag={self.tag!r}",
            f"identifier={self.identifier!r}",
            f"data={self.data!r}",
        )
        return f"{name}({', '.join(kwargs)})"

    def __lt__(self, other):
        return self.tag < other.tag

    def _set_identifier(self, nid):
        """Initialize self._set_identifier"""
        if nid is None:
            self._identifier = str(uuid.uuid1())
        else:
            self._identifier = nid

    @property
    def bpointer(self):
        """Return the value of `_bpointer`."""
        return self._bpointer

    @bpointer.setter
    def bpointer(self, nid):
        """Set the value of `_bpointer`."""
        self._bpointer = nid

    @property
    def fpointer(self):
        """Return the value of `_fpointer`."""
        return self._fpointer

    @fpointer.setter
    def fpointer(self, value):
        """Set the value of `_fpointer`."""
        if value is None:
            self._fpointer = list()
        elif isinstance(value, (Sequence, Set)):
            self._fpointer = list(value)
        elif isinstance(value, MutableMapping):
            self._fpointer = list(value.keys())
        else:
            raise ValueError('Sequence, Set or MutableMapping '
                             'are allowed values for fpointer only.')

    @property
    def identifier(self):
        """Return the value of `_identifier`."""
        return self._identifier

    @identifier.setter
    def identifier(self, value):
        """Set the value of `_identifier`."""
        if value is None:
            warnings.warn("Node ID can not be None")
        else:
            self._set_identifier(value)

    @property
    def is_leaf(self):
        """Return true if current node has no children."""
        return not self.fpointer

    @property
    def is_root(self):
        """Return true if self has no parent, i.e. as root."""
        return self._bpointer is None

    @property
    def tag(self):
        """Return the value of `_tag`."""
        return self._tag

    @tag.setter
    def tag(self, value):
        """Set the value of `_tag`."""
        self._tag = value

    def update_bpointer(self, nid):
        """Update parent node."""
        self.bpointer = nid

    def update_fpointer(self, nid, mode=ADD):
        """Update all children nodes."""
        if nid is None:
            return

        if mode is self.ADD:
            self._fpointer.append(nid)
        elif mode is self.DELETE:
            if nid in self._fpointer:
                self._fpointer.remove(nid)
