#!/usr/bin/python
# Multi Tasker

from boneless.arch.opcode import Instr
from boneless.arch.opcode import *

from spork.firmware.base import *

from spork.lib.uartIO import UART

from spork.firmware.firmware import Firmware

from spork.logger import logger

log = logger(__name__)

from spork.lib.alloc import GAlloc


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
        ma = GAlloc()
        return [
            MOVI(w.size, 10),
            ma(w.size, ret=[w.pointer]),
            uart.writeHex(w.pointer),
            uart.cr(),
        ]


firmware = MultiTask

if __name__ == "__main__":
    from spork.upload import Uploader
    import fwtest

    spork = fwtest.build(firmware)
    up = Uploader()
    up.upload(spork)
