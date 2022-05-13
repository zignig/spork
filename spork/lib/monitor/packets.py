"""
Generate and send packets to the host
"""

from boneless.arch.opcode import Instr
from boneless.arch.opcode import *

# the firmare constructs
from spork.firmware.base import *

# command stuff
from .defines import MAGIC, Commands

# the library code
from spork.lib.uartIO import UART

from spork.logger import logger

log = logger(__name__)

uart = UART()

# Remote packet interface
class SendPacket(SubR):
    params = ["command", "param1", "param2"]
    locals = ["value", "temp", "checksum"]

    def instr(self):
        w = self.w
        reg = self.reg
        return [
            Rem("reset the CRC"),
            STXA(w.temp, self.reg.crc.reset),
            MOVI(w.temp, MAGIC),
            uart.writeWord(w.temp),
            Rem("Checksum the packets"),
            STXA(w.value, self.reg.crc.reset),
            STXA(w.command, self.reg.crc.word),
            uart.writeWord(w.command),
            STXA(w.param1, self.reg.crc.word),
            uart.writeWord(w.param1),
            STXA(w.param2, self.reg.crc.word),
            uart.writeWord(w.param2),
            LDXA(w.checksum, self.reg.crc.crc),
            uart.writeWord(w.checksum),
        ]


sp = SendPacket()


class SendHelloResp(SubR):
    params = ["param1", "param2"]
    locals = ["magic", "command"]
    ret = ["status"]

    def instr(self):
        w = self.w
        return [
            MOVI(w.command, Commands.ok),
            sp(w.command, w.param1, w.param2),
        ]


class SendNoResp(SubR):
    params = ["param1", "param2"]
    locals = ["command", "zero"]
    ret = ["status"]

    def instr(self):
        w = self.w
        return [
            MOVI(w.command, Commands.no_command),
            sp(w.command, w.param1, w.param2),
        ]


class SendErrorResp(SubR):
    params = ["param1", "param2"]
    locals = ["magic", "command", "zero"]
    ret = ["status"]

    def instr(self):
        w = self.w
        return [
            MOVI(w.command, Commands.error),
            sp(w.command, w.param1, w.param2),
        ]


class RecievePacket(SubR):
    ret = ["command", "param1", "param2", "status"]
    locals = ["checksum", "temp"]

    def instr(self):
        w = self.w
        ll = LocalLabels()
        return [
            Rem("Reset the CRC"),
            STXA(w.temp, self.reg.crc.reset),
            MOVI(w.status, 0),
            MOVI(w.command, 0),
            MOVI(w.param1, 0),
            MOVI(w.param2, 0),
            uart.readWord(ret=[w.temp, w.status]),
            CMPI(w.status, 0),
            BNE(ll.exit),
            CMPI(w.temp, MAGIC),
            BNE(ll.bad_magic),
            uart.readWord(ret=[w.command, w.status]),
            CMPI(w.status, 0),
            BNE(ll.exit),
            STXA(w.command, self.reg.crc.word),
            uart.readWord(ret=[w.param1, w.status]),
            CMPI(w.status, 0),
            BNE(ll.exit),
            STXA(w.param1, self.reg.crc.word),
            uart.readWord(ret=[w.param2, w.status]),
            CMPI(w.status, 0),
            BNE(ll.exit),
            STXA(w.param2, self.reg.crc.word),
            uart.readWord(ret=[w.checksum, w.status]),
            CMPI(w.status, 0),
            BNE(ll.exit),
            LDXA(w.temp, self.reg.crc.crc),
            CMP(w.temp, w.checksum),
            BEQ(ll.exit),
            Rem("Bad Checksum"),
            MOVI(w.status, Commands.crc_error),
            J(ll.exit),
            ll("bad_magic"),
            MOVI(w.status, Commands.error),
            ll("exit"),
        ]


class Transport:
    Send = SendPacket()
    Recv = RecievePacket()
    Hello = SendHelloResp()
    Error = SendErrorResp()
    NoComm = SendNoResp()
    # Send.mark()
    # Recv.mark()
