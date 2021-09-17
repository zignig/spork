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


class tick(Firmware):
    def setup(self):
        " registers in the bottom Window "
        self.w.req(
            ["temp", "counter", "address", "checksum", "incoming_word", "status"]
        )

    def prelude(self):
        " code before the main loop "
        return []

    # Code objects need to return a list of ASM instructions to do stuff.
    def instr(self):
        w = self.w
        reg = self.reg
        ll = LocalLabels()
        uart = UART()
        self.stringer.boop = "BOOP"

        return [LDXA(w.temp, reg.systick.value), uart.writeHex(w.temp), uart.cr()]


" load this "
firmware = tick

if __name__ == "__main__":
    from spork.upload import Uploader
    import fwtest

    spork = fwtest.build(firmware, detail=False)
    up = Uploader()
    up.upload(spork)
