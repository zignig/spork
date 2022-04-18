#!/usr/bin/python
# testing for tree structures

from boneless.arch.opcode import Instr
from boneless.arch.opcode import *

from spork.firmware.base import *

from spork.lib.uartIO import UART

from spork.lib.tree import Tree, ShowTree

from spork.firmware.firmware import Firmware

from spork.logger import logger

log = logger(__name__)


def descend_children():
    pass


class TreeTest(Firmware):
    "Take the firmware registers and make them into tree"
    " WORKS!!! 20220410 "

    def setup(self):
        self.w.req(["temp", "counter", "wait", "depth"])
        # Create the tree structures
        m = self.m = Tree("reg")
        reg = self.reg

        def recurse(item, m):
            if type(item) == int:
                return
            # if type(item) == type(int):
            #     return
            for i, j in item._children.items():
                sub = m.add(i)
                recurse(j, sub)

        recurse(reg, m)
        # sub = m.add("hello", None)
        # un2 = m.add("two", None)
        # for i in range(20):
        #     un2.add('added'+str(i))
        # m.add("three", None)
        # m.add("four",None)
        # sub.add("test", None)
        # un = sub.add("fnord", None)
        # for i in range(10):
        #     un2.add("again" + str(i ), None)
        # un.add("longer")

    def prelude(self):
        return []

    # def extra(self):
    #    return self.m.code()

    def instr(self):
        w = self.w
        reg = self.reg
        ll = LocalLabels()
        uart = UART()
        sm = ShowTree()
        ll = LocalLabels()
        return [
            self.m(w.temp),
            MOVI(w.depth, 0),
            sm(w.temp, w.depth),
            ll("again"),
            J(ll.again),
        ]


firmware = TreeTest

if __name__ == "__main__":
    from spork.upload import Uploader
    import fwtest

    spork = fwtest.build(firmware)
    up = Uploader()
    up.upload(spork)
