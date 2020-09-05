#!/usr/bin/python
# minimal firmware the boneless, dump the char set and blink a light.

from boneless.arch.opcode import Instr
from boneless.arch.opcode import *

from spork.firmware.base import *

from spork.lib.uartIO import UART

from spork.firmware.firmware import Firmware

from spork.logger import logger

log = logger(__name__)


class CharSplash(Firmware):
    def setup(self):
        " registers in the bottom Window "
        self.w.req(["temp", "counter", "wait", "value"])

    def prelude(self):
        return []

    def instr(self):
        " Locals and the attached subroutine in the main loop "
        w = self.w
        reg = self.reg
        ll = LocalLabels()
        # create the subroutine
        uart = UART()

        return [
            MOVI(w.counter, 0),
            ll("loop"),
            ADDI(w.counter, w.counter, 1),
            STXA(w.counter, reg.treg.test),
            LDXA(w.value, reg.treg.test),
            uart.writeHex(w.value),
            uart.cr(),
            J(ll.loop),
        ]


firmware = CharSplash

if __name__ == "__main__":
    from spork.upload import Uploader
    import fwtest

    spork = fwtest.build(firmware)
    up = Uploader()
    up.upload(spork)
