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
        " grab the named register window for local use"
        w = self.w
        " local reference to this list of named registers for the peripherals"
        reg = self.reg
        " make a set of local labels that will not collide "
        ll = LocalLabels()
        " create a instance of ASM subroutines , they only get included if they are used"
        uart = UART()

        return [
            Rem("there is a main loop around these instrutions"),
            Rem("start at space, ignore control char"),
            MOVI(w.counter, 32),
            Rem("enable and , turn on the led"),
            MOVI(w.temp, 1),
            STXA(w.temp, reg.statusled.en),
            ll("loop"),
            Rem("write the char to the uart"),
            uart.write(w.counter),
            Rem("invert the led"),
            XORI(w.temp, w.temp, 0xFFFF),
            STXA(w.temp, reg.statusled.led),
            Rem("Delay loop"),
            MOVI(w.wait, 0xAFFF),
            ll("wait"),
            SUBI(w.wait, w.wait, 1),
            CMPI(w.wait, 0),
            BNE(ll.wait),
            Rem("End delay loop"),
            Rem("Increment the char counter"),
            ADDI(w.counter, w.counter, 1),
            Rem("are at the end of the printable chars?"),
            CMPI(w.counter, 125),
            BNE(ll.loop),
            Rem("and around again, Firmware has builtin main loop"),
        ]


firmware = CharSplash

if __name__ == "__main__":
    from spork.upload import Uploader
    import fwtest

    spork = fwtest.build(firmware)
    up = Uploader()
    up.upload(spork)
