#!/usr/bin/python
# minimal shell for the boneless

from boneless.arch.opcode import Instr
from boneless.arch.opcode import *

from spork.firmware.base import *

from spork.lib.uartIO import UART
from spork.lib.stringer import Stringer
from spork.firmware.firmware import Firmware

from spork.logger import logger

from nmigen_boards.resources.interface import UARTResource
from nmigen.build import Resource, Subsignal, Pins, Attrs

log = logger(__name__)


"""
USB test harness
"""


class USBHarness(Firmware):
    def setup(self):
        " registers in the bottom Window "
        self.w.req(["value", "status", "temp", "counter"])

    def prelude(self):
        return []

    def instr(self):
        " Locals and the attached subroutine in the main loop "
        w = self.w
        reg = self.reg
        ll = LocalLabels()
        # create the subroutine
        uart = UART()

        return [
            ll("loop"),
            ll("wait"),
            LDXA(w.status, reg.acm.rx.rdy),
            # uart.writeHex(w.status),
            CMPI(w.status, 1),
            BNE(ll.wait),
            LDXA(w.value, reg.acm.rx.data),
            uart.write(w.value),
            # ll('wait_tx'),
            # LDXA(w.status, reg.acm.tx.rdy),
            # CMPI(w.status,1),
            # BNE(ll.wait_tx),
            # STXA(w.value,reg.acm.tx.data),
            J(ll.loop),
        ]


firmware = USBHarness

if __name__ == "__main__":
    from spork.upload import Uploader
    from luna_test import UPPER, TinyFPGABxPlatform

    pl = TinyFPGABxPlatform()
    pl.add_resources(
        [
            UARTResource(
                0, rx="A8", tx="B8", attrs=Attrs(IO_STANDARD="SB_LVCMOS", PULLUP=1)
            ),
            Resource("reset_pin", 0, Pins("18", conn=("gpio", 0), dir="i")),
            # *ButtonResources(pins="10", invert=True, attrs=Attrs(IO_STANDARD="SB_LVCMOS")),
        ]
    )

    spork = UPPER(pl, firmware)
    up = Uploader()
    up.upload(spork.spork)
