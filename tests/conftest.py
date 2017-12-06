import pytest

from ttree import Tree, Node


@pytest.fixture
def node1():
    return Node("Test One", "identifier 1")


@pytest.fixture
def node2():
    return Node("Test Two", "identifier 2")


@pytest.fixture
def tree():
    result = Tree()
    result.create_node("Hárry", "hárry")
    result.create_node("Jane", "jane", parent="hárry")
    result.create_node("Bill", "bill", parent="hárry")
    result.create_node("Diane", "diane", parent="jane")
    result.create_node("George", "george", parent="bill")
    """
    Hárry
    ├── Bill
    │   └── George
    └── Jane
        └── Diane
    """
    return result


@pytest.fixture
def tree_as_string():
    return """\
Hárry
|-- Jane
|   +-- Diane
+-- Bill
    +-- George
"""

@pytest.fixture
def copytree(tree):
    return Tree(tree, True)
