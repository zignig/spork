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


class MonitorFirm(Firmware):
    def setup(self):
        pass


" load this "
firmware = MonitorFirm

if __name__ == "__main__":
    from spork.upload import Uploader
    import fwtest

    spork = fwtest.build(firmware, detail=False)
    up = Uploader()
    up.upload(spork)
