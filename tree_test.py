#!/usr/bin/python
# minimal firmware the boneless, dump the char set and blink a light.

from boneless.arch.opcode import Instr
from boneless.arch.opcode import *

from spork.firmware.base import *

from spork.lib.uartIO import UART
from spork.lib.tree import Menu

from spork.firmware.firmware import Firmware

from spork.logger import logger

log = logger(__name__)


class TreeTest(Firmware):
    def setup(self):
        " registers in the bottom Window "
        self.w.req(["temp", "counter", "wait", "dur"])
        m = self.m = Menu("testing")
        sub = m.add("hello", None)
        m.add("two", None)
        m.add("three", None)
        sub.add("test", None)
        un = sub.add("fnord", None)
        for i in range(10):
            un.add("again", None)

    def prelude(self):
        return []

    def extra(self):
        return self.m.code()

    def instr(self):
        w = self.w
        reg = self.reg
        ll = LocalLabels()
        uart = UART()

        return [[]]


firmware = TreeTest

if __name__ == "__main__":
    from spork.upload import Uploader
    import fwtest

    spork = fwtest.build(firmware)
    up = Uploader()
    up.upload(spork)
