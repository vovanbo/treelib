from enum import Enum


class ASCIIMode(Enum):
    simple = ('|', '|-- ', '+-- ')
    ex = ('│', '├── ', '└── ')
    exr = ('│', '├── ', '╰── ')
    em = ('║', '╠══ ', '╚══ ')
    emv = ('║', '╟── ', '╙── ')
    emh = ('│', '╞══ ', '╘══ ')