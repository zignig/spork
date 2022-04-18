#!/usr/bin/python
# minimal firmware the boneless, dump the char set and blink a light.

from boneless.arch.opcode import Instr
from boneless.arch.opcode import *

from spork.firmware.base import *

from spork.lib.uartIO import UART

from spork.firmware.firmware import Firmware

from spork.logger import logger

log = logger(__name__)


class Get(SubR):
    params = ["size"]
    locals = ["current", "next", "end"]
    ret = ["next"]

    def setup(self):
        pass

    def instr(self):
        w = self.w
        return [self.globals.base(w.current), ADD(w.next, w.current, w.size)]


class Alloc(Firmware):
    def setup(self):
        "registers in the bottom Window"
        self.w.req(["temp", "pos", "counter", "wait", "size", "pointer"])

    def prelude(self):
        return []

    def instr(self):
        "Locals and the attached subroutine in the main loop"
        w = self.w
        reg = self.reg
        ll = LocalLabels()
        get = Get()
        # create the subroutine
        self.globals.base = 0
        uart = UART()

        return [
            MOVR(w.temp, self.labels.heap_start),
            self.globals.base(w.pos),
            ST(w.temp, w.pos, 0),
            MOVI(w.size, 100),
            get(w.size, ret=[w.pointer]),
        ]


firmware = Alloc

if __name__ == "__main__":
    from spork.upload import Uploader
    import fwtest

    spork = fwtest.build(firmware)
    up = Uploader()
    up.upload(spork)
