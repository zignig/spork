"Console"

from boneless.arch.opcode import Instr
from boneless.arch.opcode import *

from ..firmware.base import *

from .stringer import Stringer
from .switch import Switch
from .uartIO import UART
from .action_list import Actions
from .commands import MetaCommand

from ..logger import logger

log = logger(__name__)

from rich import print


class Action(SubR):
    # Actions from the console
    def setup(self):
        self.params = ["pad_address", "status"]
        self.locals = ["temp"]
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
        # make a CASE style selection
        sel = self.selector
        sel.add(
            (
                Actions.RUN,  # CR for now
                [
                    Rem("Just echo out the pad"),
                    uart.cr(),
                    uart.writestring(w.pad_address),
                    MOVI(w.status, 0),
                    Rem("Reset the pad"),
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
                [self.stringer.escape(w.temp), uart.writestring(w.temp)],
            )
        )
        sel.add((Actions.COMPLETE, [List(), uart.cr()]))  # complete
        return [sel()]


if __name__ == "__main__":
    log.critical("Action Testing")
