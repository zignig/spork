#!/usr/bin/python
# Multi Tasker

from boneless.arch.opcode import Instr
from boneless.arch.opcode import *

from spork.firmware.base import *

from spork.lib.uartIO import UART

from spork.firmware.firmware import Firmware

from spork.logger import logger

log = logger(__name__)

from spork.lib.alloc import ModAlloc


class MultiTask(Firmware):
    def setup(self):
        " registers in the bottom Window "
        self.w.req(["temp", "counter", "pointer", "dur", "size"])

    def prelude(self):
        return []

    def instr(self):
        w = self.w
        reg = self.reg
        ll = LocalLabels()
        uart = UART()
        ma = ModAlloc()
        return [
            MOVI(w.temp, 200),
            MOVI(w.size, 10),
            ma(w.temp, w.size, ret=[w.temp, w.pointer]),
        ]


firmware = MultiTask

if __name__ == "__main__":
    from spork.upload import Uploader
    import fwtest

    spork = fwtest.build(firmware)
    up = Uploader()
    up.upload(spork)
