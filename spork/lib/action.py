"Actions to run on the console"

from boneless.arch.opcode import Instr
from boneless.arch.opcode import *

from ..firmware.base import *

from .stringer import Stringer
from .switch import Switch
from .uartIO import UART
from .action_list import Actions
from .commands import MetaCommand
from .ansi_codes import Term

from ..logger import logger

log = logger(__name__)

from rich import print

term = Term()


class Action(SubR):
    " Action switch from the console status"

    def setup(self):
        self.params = ["pad_address", "status"]
        self.locals = ["temp", "command"]
        self.ret = ["status"]

    def build(self):
        # Bind the pad into the function
        self.selector = Switch(self.w, self.w.status)

    def instr(self):
        w = self.w
        reg = self.reg
        ll = LocalLabels()
        uart = UART()
        List = MetaCommand.List()
        Search = MetaCommand.Search()
        Run = MetaCommand.Run()
        # make a CASE style selection
        sel = self.selector
        self.stringer.notfound = "Command not found :"
        sel.add(
            (
                Actions.RUN,  # find a command if any and run.
                [
                    Rem("Search for a matching command and run"),
                    Rem("Check for empty command"),
                    LD(w.temp, w.pad_address, 0),
                    CMPI(w.temp, 0),
                    BZ(ll.cont),
                    uart.cr(),
                    Search(w.pad_address, ret=[w.status, w.command]),
                    CMPI(w.status, 1),
                    BNE(ll.skip),
                    # uart.writeHex(w.command),
                    Rem("Reset the pad"),
                    MOVI(w.status, 0),
                    ST(w.status, w.pad_address, 0),
                    Rem("Found a command run"),
                    Run(w.command),
                    J(ll.cont),
                    ll("skip"),
                    self.stringer.notfound(w.temp),
                    uart.writestring(w.temp),
                    ll("cont"),
                    uart.writestring(w.pad_address),
                    Rem("Reset the pad"),
                    MOVI(w.status, 0),
                    ST(w.status, w.pad_address, 0),
                    uart.cr(),
                    self.stringer.prompt(self.w.temp),
                    uart.writestring(self.w.temp),
                ],
            )
        )
        sel.add(
            (
                Actions.ESCAPE,  # escape sequence
                [
                    Rem("write the escape sequence"),
                    self.stringer.escape(w.temp),
                    uart.writestring(w.temp),
                ],
            )
        )
        sel.add(
            (
                Actions.BACKSPACE,  # escape sequence
                [
                    self.stringer.backspace(w.temp),
                    uart.writestring(w.temp),
                    # self.stringer.clearline(w.temp),
                    # term(w.temp),
                    # self.stringer.start(w.temp),
                    # term(w.temp),
                ],
            )
        )
        sel.add(
            (
                Actions.COMPLETE,  # tab complete
                [
                    Rem("list all commands"),
                    List(),
                    self.stringer.prompt(self.w.temp),
                    uart.writestring(self.w.temp),
                    uart.writestring(w.pad_address),
                ],
            )
        )
        return [sel()]


if __name__ == "__main__":
    log.critical("Action Testing")
