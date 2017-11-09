from enum import Enum


class ASCIIMode(Enum):
    simple = ('|', '|-- ', '+-- ')
    ex = ('│', '├── ', '└── ')
    exr = ('│', '├── ', '╰── ')
    em = ('║', '╠══ ', '╚══ ')
    emv = ('║', '╟── ', '╙── ')
    emh = ('│', '╞══ ', '╘══ ')


class TraversalMode(Enum):
    DEPTH = 'depth'
    WIDTH = 'width'
    ZIGZAG = 'zigzag'
