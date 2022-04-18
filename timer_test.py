#!/usr/bin/python

# the instruction set
# TODO port to allocator IR
from boneless.arch.opcode import Instr
from boneless.arch.opcode import *

# the firmare constructs
from spork.firmware.base import *

# the library code
from spork.lib.uartIO import UART
from spork.lib.ansi_codes import AnsiStrings, Term
from spork.firmware.firmware import Firmware

from spork.lib.alloc import Alloc

# command infrastructure
from spork.logger import logger

log = logger(__name__)


"""
"""


class Info(SubR):
    def setup(self):
        self.locals = ["temp"]

    def instr(self):
        w = self.w
        reg = self.reg
        uart = UART()
        return [
            uart.sp(),
            LDXA(w.temp, reg.systick.interval),
            uart.writeHex(w.temp),
            uart.sp(),
            LDXA(w.temp, reg.systick.multiplier),
            uart.writeHex(w.temp),
        ]


# TODO convert to inline
class Init(Inline):
    "Run this code on reset , device init"
    # TODO find best way to attach this to the peripherals.
    def instr(self):
        w = self.w
        reg = self.reg
        self.globals.heap = 0
        return [
            Rem("load the timer"),
            MOVI(w.temp, 0x0001),
            STXA(w.temp, reg.timer.reload_0),
            MOVI(w.temp, 0x00FF),
            STXA(w.temp, reg.timer.reload_1),
            Rem("enable timer and events"),
            MOVI(w.temp, 1),
            STXA(w.temp, reg.timer.en),
            STXA(w.temp, reg.timer.ev.enable),
        ]


class Small(Firmware):
    def setup(self):
        "registers in the bottom Window"
        self.w.req(["temp", "counter", "address", "checksum", "other", "status"])

    def prelude(self):
        "code before the main loop"
        i = Init(self.w)
        return i()

    # Code objects need to return a list of ASM instructions to do stuff.
    def instr(self):
        w = self.w
        reg = self.reg
        ll = LocalLabels()
        info = Info()
        uart = UART()
        self.stringer.boop = "BOOP"

        " some global _fixed_ references "
        # TODO make globals typesafe

        return [
            MOVI(w.other, 0x0040),
            STXA(w.other, reg.systick.multiplier),
            MOVI(w.other, 0xFFFF),
            STXA(w.other, reg.systick.interval),
            ll("again"),
            LDXA(w.temp, reg.systick.ev.pending),
            CMPI(w.temp, 1),
            BNE(ll.over),
            MOVI(w.temp, 1),
            STXA(w.temp, reg.systick.ev.pending),
            self.stringer.boop(w.temp),
            uart.writestring(w.temp),
            info(),
            uart.cr(),
            # LDXA(w.other,reg.systick.interval),
            # SUBI(w.other,w.other,256),
            # STXA(w.other,reg.systick.interval),
            ll("over"),
            ADDI(w.counter, w.counter, 1),
            uart.writeHex(w.counter),
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
