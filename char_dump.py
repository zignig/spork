# minimal boot loader for the boneless

from boneless.arch.opcode import Instr
from boneless.arch.opcode import *

from ideal_spork.firmware.base import *

from uartIO import UART
from console import Console
from action import Action

from ideal_spork.firmware.stringer import Stringer
from ideal_spork.firmware.firmware import Firmware

from ideal_spork.logger import logger

log = logger(__name__)


class CharSplash(Firmware):
    def setup(self):
        " registers in the bottom Window "
        self.w.req(["counter", "wait"])

    def instr(self):
        " Locals and the attached subroutine in the main loop "
        w = self.w
        reg = self.reg
        ll = LocalLabels()
        # create the subroutine
        uart = UART()

        return [
            MOVI(w.counter, 32),
            ll("loop"),
            uart.write(w.counter),
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