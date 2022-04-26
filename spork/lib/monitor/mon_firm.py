#!/usr/bin/python


# make a firmware object
# enumerate the commands from commands
# with some spares and handle comms

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

from .packets import Transport

trans = Transport()


class OtherStuff(SubR):
    def instr(self):
        return []


class MonAction(SubR):
    locals = ["command", "param1", "param2", "status"]

    def instr(self):
        w = self.w
        return [
            trans.Recv(ret=[w.command, w.param1, w.param2, w.status]),
            trans.Hello(),
        ]


# Working Functions``
os = OtherStuff()
ma = MonAction()


class MonitorFirm(Firmware):
    def setup(self):
        self.w.req(["value"])

    def instr(self):
        w = self.w
        reg = self.reg
        ll = LocalLabels()
        return [
            Rem("Loop and Wait for serial"),
            LDXA(w.value, reg.serial.rx.rdy),
            CMPI(w.value, 0),
            BEQ(ll.over),
            ma(),
            ll("over"),
            os(),
        ]


" load this "
firmware = MonitorFirm

if __name__ == "__main__":
    from spork.upload import Uploader
    import fwtest

    spork = fwtest.build(firmware, detail=False)
    up = Uploader()
    up.upload(spork, console=False)
