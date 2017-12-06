Usage
=====


Basic Usage
-----------

.. code-block:: python

    >>> from ttree import Node, Tree
    >>> tree = Tree()
    >>> tree.create_node("Harry", "harry")  # root node
    >>> tree.create_node("Jane", "jane", parent="harry")
    >>> tree.create_node("Bill", "bill", parent="harry")
    >>> tree.create_node("Diane", "diane", parent="jane")
    >>> tree.create_node("Mary", "mary", parent="diane")
    >>> tree.create_node("Mark", "mark", parent="jane")
    >>> tree.print()
    Harry
    ├── Jane
    │   ├── Diane
    │   │   └── Mary
    │   └── Mark
    └── Bill


API Examples
------------

**Example 1**: Expand a tree with specific mode (Tree.DEPTH [default],
Tree.WIDTH, Tree.ZIGZAG).

.. code-block:: python

    >>> print(','.join([tree[node].tag for node in tree.expand_tree(mode='depth')]))
    Harry,Bill,Jane,Diane,Mary,Mark

**Example 2**: Expand tree with custom filter.

.. code-block:: python

    >>> print(','.join(
              [tree[node].tag for node in
               tree.expand_tree(filtering=lambda x: x.id != 'diane')]))
    Harry,Bill,Jane,Mark

**Example 3**: Get a subtree with the root of 'diane'.

.. code-block:: python

    >>> sub_t = tree.subtree('diane')
    >>> sub_t.print()
    Diane
    └── Mary

**Example 4**: Paste a new tree to the original one.

.. code-block:: python

    >>> new_tree = Tree()
    >>> new_tree.create_node("n1", 1)  # root node
    >>> new_tree.create_node("n2", 2, parent=1)
    >>> new_tree.create_node("n3", 3, parent=1)
    >>> tree.paste('bill', new_tree)
    >>> tree.print()
    Harry
    ├── Jane
    │   ├── Diane
    │   │   └── Mary
    │   └── Mark
    └── Bill
        └── n1
            ├── n2
            └── n3

**Example 5**: Remove the existing node from the tree

.. code-block:: python

    >>> tree.remove_node(1)
    >>> tree.print()
    Harry
    ├── Jane
    │   ├── Diane
    │   │   └── Mary
    │   └── Mark
    └── Bill

**Example 6**: Move a node to another parent.

.. code-block:: python

    >>> tree.move_node('mary', 'harry')
    >>> tree.print()
    Harry
    ├── Jane
    │   ├── Diane
    │   └── Mark
    ├── Bill
    └── Mary

**Example 7**: Get the height of the tree.

.. code-block:: python

    >>> tree.depth()
    2

**Example 8**: Get the level of a node.

.. code-block:: python

    >>> node = tree.get("bill")
    >>> tree.depth(node)
    1

**Example 9**: Print or dump tree structure. For example, the same tree in
 basic example can be printed with 'em':

.. code-block:: python

    >>> tree.print(ascii_mode='em')
    Harry
    ╠══ Jane
    ║   ╠══ Diane
    ║   ╚══ Mark
    ╠══ Bill
    ╚══ Mary


In the JSON form, to_json() takes optional parameter with_data to trigger if
the data field is appended into JSON string. For example,

.. code-block:: python

    >>> print(tree.to_json(with_data=True))
    {"Harry": {"children": [{"Bill": {"data": null}}, {"Jane": {"children": [{"Diane": {"data": null}}, {"Mark": {"data": null}}], "data": null}}, {"Mary": {"data": null}}], "data": null}}


Advanced Usage
--------------

Sometimes, you need trees to store your own data. The newsest version of
:mod:`ttree` supports ``.data`` variable to store whatever you want. For
example, to define a flower tree with your own data:

.. code-block:: python

    >>> class Flower(object): \
            def __init__(self, color): \
                self.color = color

You can create a flower tree now:

.. code-block:: python

    >>> ftree = Tree()
    >>> ftree.create_node("Root", "root", data=Flower("black"))
    >>> ftree.create_node("F1", "f1", parent='root', data=Flower("white"))
    >>> ftree.create_node("F2", "f2", parent='root', data=Flower("red"))

Printing the colors of the tree:

.. code-block:: python

    >>> ftree.print(data_property="color")
    black
    ├── white
    └── red


Additional examples
-------------------

The following advanced examples are placed in repo:

* `Family Tree <https://github.com/vovanbo/ttree/blob/master/examples/family_tree.py>`_
* `Folder Tree <https://github.com/vovanbo/ttree/blob/master/examples/folder_tree.py>`_
* `Recursive directory tree <https://github.com/vovanbo/ttree/blob/master/examples/recursive_dirtree_generator.py>`_
