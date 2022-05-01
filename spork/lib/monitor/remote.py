# remote commands to run on the processor

# version
# data packets
# send recieve

from boneless.arch.opcode import Instr
from boneless.arch.opcode import *

# the firmare constructs
from ...firmware.base import *

from ..switch import Switch

from spork.logger import logger

log = logger(__name__)

from .packets import Transport
from .commands import CL
from .defines import FIRMWARE_VERSION, GATEWARE_VERSION, Commands

from spork.lib.uartIO import UART

# The uart instance
uart = UART()


class ReadData(SubR):
    """
    read word data into a memory block
    has checksum as the last word ,
    checks on the way through
    (soon) rechecks the memory in place.
    """

    params = ["address", "size"]
    locals = ["counter", "dest", "value"]
    ret = ["status"]

    def instr(self):
        w = self.w
        ll = LocalLabels()
        return [
            Rem("Put data into memory"),
            MOVI(w.counter, 0),
            MOVI(w.status, 0),
            MOV(w.dest, w.address),
            STXA(w.counter, self.reg.crc.reset),
            ll("again"),
            uart.readWord(ret=[w.value, w.status]),
            CMPI(w.status, 0),
            BNE(ll.exit),  # status bubbles up
            Rem("Store in memory"),
            ST(w.value, w.address, 0),
            Rem("update the checksum"),
            STXA(w.value, self.reg.crc.word),
            Rem("increment the counters"),
            ADDI(w.counter, w.counter, 1),
            ADDI(w.address, w.address, 1),
            CMP(w.counter, w.size),
            BNE(ll.again),
            uart.readWord(ret=[w.value, w.status]),
            CMPI(w.status, 0),
            BNE(ll.exit),
            Rem("Borrow status register for crc"),
            LDXA(w.status, self.reg.crc.crc),
            CMP(w.status, w.value),
            BNE(ll.crc_error),
            ll("cont"),
            # TODO , recheck memory against checksum
            J(ll.exit),
            ll("crc_error"),
            MOVI(w.status, Commands.crc_error),
            ll("exit"),
        ]


class WriteData(SubR):
    params = ["address", "size"]
    locals = ["counter", "value", "checksum"]
    ret = ["status"]

    def instr(self):
        w = self.w
        ll = LocalLabels()
        return [
            MOVI(w.counter, 0),
            MOVI(w.status, 0),
            STXA(w.counter, self.reg.crc.reset),
            ll("again"),
            LD(w.value, w.address, 0),
            uart.writeWord(w.value),
            STXA(w.value, self.reg.crc.word),
            Rem("increment the counters"),
            ADDI(w.counter, w.counter, 1),
            ADDI(w.address, w.address, 1),
            CMP(w.counter, w.size),
            BNE(ll.again),
            LDXA(w.checksum, self.reg.crc.crc),
            uart.writeWord(w.checksum),
        ]


class VersionInformation(CodeObject):
    "Put the version and system information in a datablock"
    " "

    def __init__(self):
        super().__init__()
        self.version = FIRMWARE_VERSION
        self.gateway = GATEWARE_VERSION
        self.dummy = 0xAAAA

    def code(self):
        "8 items , one window"
        return [
            self.version,
            self.gateway,
            self.dummy,
            self.dummy,
            self.dummy,
            self.dummy,
            self.dummy,
            self.dummy,
        ]


class GetVersion(SubR):
    "Get mon version , gateway version , freewords , and stuff"
    locals = ["counter"]

    def instr(self):
        w = self.w
        ll = LocalLabels()
        return []


class DataBlock:
    Write = WriteData()
    Read = ReadData()
    Version = GetVersion()
