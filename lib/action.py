"Console"

from boneless.arch.opcode import Instr
from boneless.arch.opcode import *

from ideal_spork.firmware.base import *
from ideal_spork.firmware.stringer import Stringer
from switch import Switch
from uartIO import UART

from ideal_spork.logger import logger

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
        # make a CASE style selection
        sel = self.selector
        sel.add(
            (
                20,  # CR for now
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
        return [sel()]


if __name__ == "__main__":
    log.critical("Action Testing")
