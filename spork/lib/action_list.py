" Enuemerations of the commands for symbolic reference"

from enum import IntEnum, auto


class Actions(IntEnum):
    " Enumeration of console actions"
    NONE = auto()
    RUN = auto()
    ESCAPE = auto()
    COMPLETE = auto()
    BACKSPACE = auto()


class EscKeys(IntEnum):
    " Convert Escape sequences into an Integer"
    ESC = auto()
    INS = auto()
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()
    # BackSpace is not an escape but enumerate anyway
    # for the better
    BS = auto()
    DEL = auto()
    HOME = auto()
    END = auto()
    PGUP = auto()
    PGDOWN = auto()
    F1 = auto()
    F2 = auto()
    F3 = auto()
    F4 = auto()
    F5 = auto()
    F6 = auto()
    F7 = auto()
    F8 = auto()
    F9 = auto()
    F10 = auto()
    F11 = auto()
    F12 = auto()
