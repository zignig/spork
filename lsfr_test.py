#!/usr/bin/python

# the instruction set
# TODO port to allocator IR
from boneless.arch.opcode import Instr
from boneless.arch.opcode import *

# the firmare constructs
from spork.firmware.base import *
from spork.firmware.firmware import Firmware

# the library code
from spork.lib.uartIO import UART

from spork.logger import logger

log = logger(__name__)


class Small(Firmware):
    def setup(self):
        self.w.req(["temp", "counter", "address", "value", "other", "status"])

    # Code objects need to return a list of ASM instructions to do stuff.
    def instr(self):
        w = self.w
        reg = self.reg
        ll = LocalLabels()

        uart = UART()

        return [
            MOVI(w.other, 1),
            STXA(w.other, reg.lsfr.mode),
            MOVI(w.other, 0x00FF),
            STXA(w.other, reg.lsfr.value),
            ll("again"),
            uart.readWait(ret=[w.value]),
            [uart.writeHex(w.value), uart.cr(), uart.cr()],
            LDXA(w.temp, reg.lsfr.value),
            uart.writeHex(w.temp),
            uart.cr(),
            J(ll.again),
        ]


" load this "
firmware = Small

if __name__ == "__main__":
    from spork.upload import Uploader
    import fwtest

    spork = fwtest.build(firmware, detail=False)
    up = Uploader()
    up.upload(spork)
