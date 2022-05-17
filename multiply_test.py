#!/usr/bin/python

# the instruction set
# TODO port to allocator IR
from re import I
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
        self.w.req(["opa", "opb", "res1", "res2", "other", "status"])

    # Code objects need to return a list of ASM instructions to do stuff.
    def instr(self):
        w = self.w
        reg = self.reg
        ll = LocalLabels()
        self.stringer.second = "multiply"
        uart = UART()

        return [
            MOVI(w.opa, 1),
            MOVI(w.opb, 99),
            ll("loop"),
            STXA(w.opa, reg.multiply.opa),
            STXA(w.opb, reg.multiply.opb),
            LDXA(w.res1, reg.multiply.result_1),
            LDXA(w.res2, reg.multiply.result_0),
            uart.writeHex(w.res1),
            uart.writeHex(w.res2),
            uart.cr(),
            uart.readWait(),
            ADDI(w.opa, w.opa, 1),
            J(ll.loop),
        ]


" load this "
firmware = Small

if __name__ == "__main__":
    from spork.upload import Uploader
    import fwtest

    spork = fwtest.build(firmware, detail=False)
    up = Uploader()
    up.upload(spork)
