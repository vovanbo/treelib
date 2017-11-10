class NodeNotFound(Exception):
    """Exception raises if a node's identifier is unknown"""
    pass


class NodePropertyNotFound(Exception):
    """Exception raises if a node's data property is not specified"""
    pass


class MultipleRoots(Exception):
    """Exception raises if more than one root exists in a tree."""
    pass


class DuplicatedNode(Exception):
    """Exception raises if an identifier already exists in a tree."""
    pass


class LinkPastRootNode(Exception):
    """
    Exception raises in Tree.link_past_node() if one attempts
    to "link past" the root node of a tree.
    """
    pass


class InvalidLevelNumber(Exception):
    pass


class LoopError(Exception):
    """
    Exception raises if trying to move node B to node A's position
    while A is B's ancestor.
    """
    pass
