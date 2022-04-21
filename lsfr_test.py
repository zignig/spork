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
        self.stringer.second = "second string"
        uart = UART()

        return [
            MOVI(w.counter, 0),
            MOVI(w.other, 1),
            STXA(w.other, reg.lsfr.mode),
            # MOVI(w.other, 0x81A5),
            # STXA(w.other, reg.lsfr.taps),
            MOVI(w.value, 0xDEAD),
            STXA(w.value, reg.lsfr.value),
            # LDXA(w.temp, reg.lsfr.value),
            # LDXA(w.temp, reg.lsfr.value),
            # uart.readWait(),
            ll("again"),
            # [uart.writeHex(w.value),  uart.cr(), uart.cr()],
            LDXA(w.temp, reg.lsfr.value),
            # uart.writeBin(w.temp),
            # uart.cr(),
            uart.writeHex(w.counter),
            uart.sp(),
            uart.writeHex(w.temp),
            # uart.writeBin(w.temp),
            uart.cr(),
            ADDI(w.counter, w.counter, 1),
            # J(ll.again),
            CMPI(w.counter, 32),
            # CMP(w.value,w.temp),
            BNE(ll.again),
            MOVI(w.temp, 0),
            STXA(w.temp, reg.lsfr.mode),
            MOVI(w.counter, 0),
            self.stringer.second(w.other),
            uart.writestring(w.other),
            uart.cr(),
            uart.readWait(),
            ll("second"),
            LDXA(w.temp, reg.lsfr.value),
            uart.writeHex(w.temp),
            uart.sp(),
            ADDI(w.counter, w.counter, 1),
            CMPI(w.counter, 32),
            BNE(ll.second),
            uart.cr(),
            uart.readWait(),
        ]


" load this "
firmware = Small

if __name__ == "__main__":
    from spork.upload import Uploader
    import fwtest

    spork = fwtest.build(firmware, detail=False)
    up = Uploader()
    up.upload(spork)
