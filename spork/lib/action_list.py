" Enuemerations of the commands for symbolic reference"

from enum import IntEnum, auto


class Actions(IntEnum):
    NONE = auto()
    RUN = auto()
    ESCAPE = auto()
    ESCAPE_0 = auto()
    ESCAPE_1 = auto()
    ESCAPE_2 = auto()
    COMPLETE = auto()
