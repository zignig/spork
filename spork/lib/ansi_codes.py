"Ansi code for terminal goodness"

from boneless.arch.opcode import Instr
from boneless.arch.opcode import *

from ..firmware.base import *
from .stringer import Stringer
from .uartIO import UART

from ..logger import logger

log = logger(__name__)

uart = UART
from rich import print


class Term(SubR):
    def setup(self):
        self.params = ["string"]
        self.locals = ["escape", "temp"]

    def instr(self):
        w = self.w
        return [
            self.stringer.a_esc(w.temp),
            uart.writestring(w.temp),
            uart.writestring(w.string),
        ]


def AnsiStrings(s):
    s.a_esc = u"\x1b["
    # colors
    s.black = "30m"
    s.red = "31m"
    s.green = "32m"
    s.yellow = "33m"
    s.blue = "34m"
    s.magenta = "35m"
    s.cyan = "36m"
    s.white = "37m"
    s.creset = "0m"
    # clears
    s.clearscreen = "2J"
    s.clearline = "2K"
    s.home = "H"
    # moves
    s.start = "999D"
    s.left = "1D"
    s.right = "1C"
    # move bottom right
    s.br = "999;999H"
