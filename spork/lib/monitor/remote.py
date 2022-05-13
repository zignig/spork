"""
    Collection on functions for the monitor to use.
"""

# remote commands to run on the processor

# version
# data packets
# send recieve

from telnetlib import GA
from boneless.arch.opcode import Instr
from boneless.arch.opcode import *


# the firmare constructs
from ...firmware.base import *

from ..switch import Switch
from ..alloc import GAlloc
from spork.logger import logger

log = logger(__name__)

from .packets import Transport
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
    """
    Put the version and system information in a datablock
    """

    def __init__(self):
        super().__init__()
        self.version = FIRMWARE_VERSION
        self.gateway = GATEWARE_VERSION
        self.dummy = 0xAAAA
        self._used = True
        self.label = "VersionInformation"

    def __call__(self, register):
        self._used = True
        return [MOVR(register, self.label)]

    def code(self):
        "8 items , one window"
        return [
            Rem("Monitor Information Block"),
            L("VersionInformation"),
            self.version,
            self.gateway,
            self.dummy,
            self.dummy,
            self.dummy,
            self.dummy,
            self.dummy,
            self.dummy,
        ]


class Jumper(SubR):
    "Jump to given address"
    params = ["address", "size"]  # for monitor commands
    ret = ["status"]
    _called = True

    def instr(self):
        w = self.w
        return [
            J(w.address),
        ]


class GetVersion(SubR):
    "Get mon version , gateway version , freewords , and stuff"
    params = ["param1", "param2"]  # for monitor commands
    locals = ["command", "version_pointer", "size"]
    ret = ["status"]
    _called = True

    def instr(self):
        w = self.w
        ll = LocalLabels()
        self.mark()
        self.vi = VersionInformation()
        return [
            self.vi(w.version_pointer),
            MOVI(w.command, Commands.version),
            MOVI(w.param1, FIRMWARE_VERSION),
            MOVI(w.param2, GATEWARE_VERSION),
            Transport.Send(w.command, w.param1, w.param2),
            MOVI(w.size, 8),
            DataBlock.Write(w.version_pointer, w.size),
        ]


class SendDataBlock(SubR):
    params = ["address", "size"]
    locals = ["command"]
    ret = ["status"]
    _called = True

    def instr(self):
        w = self.w
        ll = LocalLabels()
        return [
            CMPI(w.size, 0),
            BNE(ll.size_good),
            MOVI(w.command, Commands.error),
            Transport.Send(w.command, w.address, w.size),
            J(ll.end),
            ll("size_good"),
            MOVI(w.command, Commands.read_data),
            Transport.Send(w.command, w.address, w.size),
            DataBlock.Read(w.address, w.size),
            ll("end"),
        ]


class GetDatablock(SubR):
    "Get datablock"
    params = ["address", "size"]  # for monitor commands
    locals = ["command"]
    ret = ["status"]
    _called = True

    def instr(self):
        w = self.w
        ll = LocalLabels()
        self.mark()
        return [
            CMPI(w.size, 0),
            BNE(ll.size_good),
            MOVI(w.command, Commands.error),
            Transport.Send(w.command, w.address, w.size),
            J(ll.end),
            ll("size_good"),
            MOVI(w.command, Commands.read_data),
            Transport.Send(w.command, w.address, w.size),
            DataBlock.Write(w.address, w.size),
            ll("end"),
        ]


class AllocBlock(SubR):
    params = ["size", "unused"]
    locals = ["address", "command"]
    ret = ["status"]
    _called = True

    def instr(self):
        w = self.w
        ll = LocalLabels()
        ga = GAlloc()
        return [
            ga(w.size, ret=[w.address]),
            SLLI(w.size, w.size, 3),
            MOVI(w.command, Commands.alloc),
            Transport.Send(w.command, w.address, w.size),
        ]


class DataBlock:
    Write = WriteData()
    Read = ReadData()
    Version = GetVersion()
