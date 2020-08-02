" Enuemerations of the commands for symbolic reference"

from enum import IntEnum, auto


class Actions(IntEnum):
    NONE = auto()
    RUN = auto()
    ESCAPE = auto()
    COMPLETE = auto()
