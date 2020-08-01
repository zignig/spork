# minimal firmware the boneless, dump the char set and blink a light.

from boneless.arch.opcode import Instr
from boneless.arch.opcode import *

from spork.firmware.base import *

from spork.lib.uartIO import UART
from spork.lib.console import Console
from spork.lib.action import Action
from spork.lib.stringer import Stringer

from spork.firmware.firmware import Firmware

from spork.logger import logger

log = logger(__name__)


class CharSplash(Firmware):
    def setup(self):
        " registers in the bottom Window "
        self.w.req(["temp", "counter", "wait"])

    def instr(self):
        " Locals and the attached subroutine in the main loop "
        w = self.w
        reg = self.reg
        ll = LocalLabels()
        # create the subroutine
        uart = UART()

        return [
            MOVI(w.counter, 32),
            MOVI(w.temp, 1),
            STXA(w.temp, reg.statusled.en),
            ll("loop"),
            uart.write(w.counter),
            XORI(w.temp, w.temp, 0xFFFF),
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
