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


def AnsiStrings(s):
    s.a_esc = u"\u001b[".encode("utf-8")
    # colors
    s.cls = "\u001b[0J"
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
    s.clearscreen = "0J"
    s.clearline = "2K"
