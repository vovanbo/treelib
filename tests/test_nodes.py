import pytest


def test_node_initialization(node1):
    assert node1.tag == "Test One"
    assert node1.id == "identifier 1"
    assert node1.expanded
    assert node1.parent is None
    assert isinstance(node1.children, list)
    assert node1.children == []
    assert node1.data is None


def test_node_repr(node1):
    assert repr(node1) == "Node(tag='Test One', id='identifier 1', data=None)"


def test_node_set_tag(node1):
    node1.tag = "Test 1"
    assert node1.tag == "Test 1"


def test_node_set_identifier(node1):
    node1.id = "ID1"
    assert node1.id == "ID1"

    with pytest.raises(ValueError):
        node1.id = None

    node1._set_id(None)
    assert node1.id.version == 1


def test_node_add_child(node1):
    node1.add_child('id 2')
    assert node1.children == ['id 2']


def test_node_parent(node2):
    node2.parent = "id 1"
    assert node2.parent == 'id 1'


def test_node_is_leaf(node1, node2):
    node1.add_child('id 2')
    node2.parent = "id 1"
    assert not node1.is_leaf
    assert node2.is_leaf


def test_node_data(node1):
    class Flower(object):
        def __init__(self, color):
            self.color = color

        def __str__(self):
            return "%s" % self.color

    node1.data = Flower("red")
    assert node1.data.color == "red"
