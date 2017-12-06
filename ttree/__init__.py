"""
Taxonomy tree data structure implementation
===========================================

`ttree` is a Python module with two primary classes: ``Node`` and
``Tree``. Tree is a self-contained structure with some nodes and
connected by branches. A tree owns merely a root, while a
node (except root) has some children and one parent.
"""
__version__ = '1.0.1'

from .tree import Tree  # noqa
from .node import Node  # noqa
