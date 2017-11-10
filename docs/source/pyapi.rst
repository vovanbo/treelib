Useful APIs
============

.. module:: treelib
    :synopsis: Tree data structure in Python.

`treelib` is a Python module with two primary classes: ``Node`` and
``Tree``. Tree is a self-contained structure with some nodes and
connected by branches. A tree owns merely a root, while a
node (except root) has some children and one parent.

*Note:* To solve string compatibility between Python 2.x and 3.x,
treelib follows the way of porting Python 3.x to 2/3. That means, all
strings are manipulated as unicode and you do not need `u''` prefix
anymore. The impacted functions include `str()`, `print()` and
`save2file()` routines. But if your data contains non-ascii
characters and Python 2.x is used, you have to trigger the
compatibility by declaring `unicode_literals` in the code:

.. code-block:: sh

    >>> from __future__ import unicode_literals


:class:`Node` Objects
---------------------

.. class:: Node([tag[, id[, expanded]]])

   A :class:`Node` object contains basic properties such as node id,
   node tag, parent node, children nodes etc., and some operations for a node.


Class attributes are:


.. currentmodule:: node


Instance attributes:


.. attribute:: id

    The unique ID of a node within the scope of a tree. This attribute can be
    accessed and modified with ``.`` and ``=`` operator respectively.


.. attribute:: tag

    The readable node name for human. This attribute can be accessed and
    modified with ``.`` and ``=`` operator respectively.


.. attribute:: parent

    The parent ID of a node. This attribute can be
    accessed and modified with ``.`` and ``=`` operator respectively.


.. attribute:: children

    With a getting operator, a list of IDs of node's children is obtained. With
    a setting operator, the value can be list, set, or dict. For list or set,
    it is converted to a list type by the package; for dict, the keys are
    treated as the node IDs.


.. attribute:: data

    User payload associated with this node.


Instance methods:

.. method:: is_leaf ()

    Check if the node has children. Return False if the ``children`` is empty
    or None.

.. method:: is_root ()

    Check if the node is the root of present tree.

.. method:: add_child (node_id)

    Add child (indicated by the ``node_id`` parameter) of a node.

.. method:: remove_child (node_id)

    Remove child (indicated by the ``node_id`` parameter) of a node.



:mod:`Tree` Objects
---------------------

.. class:: Tree(tree=None, deepcopy=False)

    The :class:`Tree` object defines the tree-like structure based on
    :class:`Node` objects. A new tree can be created from scratch without any
    parameter or a shallow/deep copy of another tree. When ``deepcopy=True``, 
    a deepcopy operation is performed on feeding ``tree`` parameter and *more
    memory is required to create the tree*.


Class attributes are:


.. currentmodule:: tree


Instance attributes:


.. attribute:: root

    Get or set the ID of the root.  This attribute can be accessed and modified
    with ``.`` and ``=`` operator respectively.


**Instance methods**:


.. method:: add_node(node[, parent])

    Add a new node object to the tree and make the parent as the root by
    default.


.. method:: children(node_id)

    Return the children (Node) list of ``node_id``. Empty list is returned if
    ``node_id`` does not exist


.. method:: create_node(tag[, id[, parent[, data]]])

    Create a new node and add it to this tree. If ``id`` is absent,
    a UUID will be generated automatically.


.. method:: depth ([node])

    Get the maximum level of this tree or the level of the given node
    (Note: the parameter is node_instance rather than node_identifier).


.. method:: expand_tree([node_id[, mode[, filter[, key[, reverse]]]]]])

    Traverse the tree nodes with different modes. ``node_id`` refers to the
    expanding point to start; ``mode`` refers to the search mode (Tree.DEPTH,
    Tree.WIDTH). ``filter`` refers to the function of one variable to act on
    the :class:`Node` object. In this manner, the traversing will not continue to
    following children of node whose condition does not pass the filter.
    ``key``, ``reverse`` are present to sort
    :class:Node objects at the same level.


.. method:: get_node(node_id)

    Get the object of the node with ID of ``node_id`` An alternative way is using
    '[]' operation on the tree. But small difference exists between them: the
    get_node() will return None if ``node_id`` is absent, whereas '[]' will raise
    ``KeyError``.


.. method:: is_branch(node_id)

    Get the children (only sons) list of the node with ID == node_id.


.. method:: leaves (node_id)

    Get leaves from given node.


.. method:: level(node_id[, filter])

    Get the node level in this tree. The level is an integer starting with '0'
    at the root. In other words, the root lives at level '0';


.. method:: link_past_node(node_id)

    Remove a node and link its children to its parent (root is not allowed).


.. method:: move_node(source, destination)

    Move node (source) from its parent to another parent (destination).


.. method:: parent (node_id)

    Obtain specific node's parent (Node instance). Return None if the parent is
    None or does not exist in the tree.


.. method:: paste(node_id, new_tree[, deepcopy])

    Paste a new tree to an existing tree, with ``node_id`` becoming the parent of the
    root of this new tree.


.. method:: paths_to_leaves()

    Use this function to get the identifiers allowing to go from the root nodes
    to each leaf. Return a list of list of identifiers, root being not omitted.


.. method:: remove_node(node_id)

    Remove a node and free the memory along with its successors.


.. method:: remove_subtree(node_id)

    Return a subtree with ``node_id`` being the root, and remove all nodes in the
    subtree from the original one.


.. method:: rsearch(node_id[, filter])

    Search the tree from ``node_id`` to the root along links reservedly. Parameter
    ``filter`` refers to the function of one variable to act on the
    :class:`Node` object.


.. method:: save2file(filename[, node_id[, level[, idhidden[, filter[, key[, reverse]]]]]]])

    Save the tree into file for offline analysis.


.. method:: print([node_id[, level[, idhidden[, filter[, key[, reverse[, line_type[, data_property]]]]]]]]])

    Print the tree structure in hierarchy style. ``node_id`` refers to the
    expanding point to start; ``level`` refers to the node level in the tree
    (root as level 0).
    ``idhidden`` refers to hiding the node ID when printing.
    ``filter`` refers to the function of one variable to act on the
    :class:`Node` object.  In this manner, the traversing will not continue to
    following children of node whose condition does not pass the filter.
    ``key``, ``reverse`` are present to sort :class:`Node` object in the same level.
    ``data_property`` refers to the property on the node data object to be printed.

    You have three ways to output your tree data, i.e., stdout with ``print()``,
    plain text file with ``save2file()``, and json string with ``to_json()``. The
    former two use the same backend to generate a string of tree structure in a
    text graph.

    *Version >= 1.2.7a*: you can also spicify the ``ascii_mode`` parameter (now
     supporting 'simple' [default], 'ex', 'exr', 'em', 'emv', 'emh')
     to the change graphical form.


.. method:: siblings(node_id)

    Get all the siblings of given node_id.


.. method:: size ([level])

    Get the number of nodes of the whole tree if ``level`` is not given.
    Otherwise, the total number of nodes at specific level is returned.


.. method:: subtree(node_id)

    Return a soft copy of the subtree with ``node_id`` being the root. The softness
    means all the nodes are shared between subtree and the original.


.. method:: to_dict([node_id[, key[, sort[, reverse[, with_data]]]]])

    Transform the whole tree into a dict.


.. method:: to_json()

    To format the tree in a JSON format.
