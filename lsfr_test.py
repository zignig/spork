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
        self.w.req(["temp", "counter", "address", "value", "other", "status"])

    # Code objects need to return a list of ASM instructions to do stuff.
    def instr(self):
        w = self.w
        reg = self.reg
        ll = LocalLabels()

        uart = UART()

        return [
            MOVI(w.counter, 0),
            MOVI(w.other, 0),
            STXA(w.other, reg.lsfr.mode),
            MOVI(w.value, 0xA0A0),
            STXA(w.value, reg.lsfr.value),
            MOVI(w.other, 0x84E2),
            STXA(w.other, reg.lsfr.taps),
            LDXA(w.temp, reg.lsfr.value),
            LDXA(w.temp, reg.lsfr.value),
            ll("again"),
            # uart.readWait(ret=[w.value]),
            # [uart.writeHex(w.value), uart.cr(), uart.cr()],
            LDXA(w.temp, reg.lsfr.value),
            # uart.writeBin(w.temp),
            # uart.cr(),
            ADDI(w.counter, w.counter, 1),
            CMP(w.temp, w.value),
            BNE(ll.again),
            uart.writeHex(w.counter),
            uart.sp(),
            # uart.writeHex(w.temp),
            uart.writeBin(w.temp),
            uart.cr(),
            ll("wait"),
            J(ll.wait),
        ]


" load this "
firmware = Small

if __name__ == "__main__":
    from spork.upload import Uploader
    import fwtest

    spork = fwtest.build(firmware, detail=False)
    up = Uploader()
    up.upload(spork)
