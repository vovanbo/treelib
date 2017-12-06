from enum import Enum


class ASCIIMode(Enum):
    simple = ('|', '|-- ', '+-- ')
    ex = ('│', '├── ', '└── ')
    exr = ('│', '├── ', '╰── ')
    em = ('║', '╠══ ', '╚══ ')
    emv = ('║', '╟── ', '╙── ')
    emh = ('│', '╞══ ', '╘══ ')


class TraversalMode(Enum):
    #: The depth-first search mode for tree.
    DEPTH = 'depth'
    #: The width-first search mode for tree.
    WIDTH = 'width'
    #: `ZIGZAG search <https://en.wikipedia.org/wiki/Tree_(data_structure)>`_
    #: mode for tree.
    ZIGZAG = 'zigzag'
