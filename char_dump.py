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
        self.w.req(["temp", "counter", "wait"])

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
            # start at space, ignore control char
            MOVI(w.counter, 32),
            # enable and , turn on the led
            MOVI(w.temp, 1),
            STXA(w.temp, reg.statusled.en),
            # there is a main loop around these instrutions
            ll("loop"),
            uart.write(w.counter),
            # invert the led
            XORI(w.temp, w.temp, 0xFFFF),
            #
            STXA(w.temp, reg.statusled.led),
            MOVI(w.wait, 0xFFFF),
            ll("wait"),
            SUBI(w.wait, w.wait, 1),
            CMPI(w.wait, 0),
            BNE(ll.wait),
            ADDI(w.counter, w.counter, 1),
            CMPI(w.counter, 125),
            BNE(ll.loop),
        ]


firmware = CharSplash

if __name__ == "__main__":
    from upload import Uploader
    import fwtest

    spork = fwtest.build(firmware)
    up = Uploader()
    up.upload(spork)
