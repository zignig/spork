"""
Generate and send packets
"""

from boneless.arch.opcode import Instr
from boneless.arch.opcode import *

# the firmare constructs
from spork.firmware.base import *

# command stuff
from .commands import MAGIC, Commands

# the library code
from spork.lib.uartIO import UART

from spork.logger import logger

log = logger(__name__)

uart = UART()


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
            STXA(w.value, self.reg.crc.word),
            uart.writeWord(w.command),
            STXA(w.value, self.reg.crc.reset),
            Rem("Check the packets"),
            STXA(w.param1, self.reg.crc.word),
            STXA(w.param2, self.reg.crc.word),
            uart.writeWord(w.param1),
            uart.writeWord(w.param2),
            LDXA(w.checksum, self.reg.crc.crc),
            uart.writeWord(w.checksum),
        ]


sp = SendPacket()


class SendHelloResp(SubR):
    locals = ["magic", "command", "zero"]

    def instr(self):
        w = self.w
        return [
            MOVI(w.command, Commands.hello),
            MOVI(w.zero, 0),
            sp(w.command, w.zero, w.zero),
        ]


class RecievePacket(SubR):
    ret = ["command", "param1", "param2", "status"]
    locals = ["checksum", "temp"]

    def instr(self):
        w = self.w
        ll = LocalLabels()
        return [
            MOVI(w.status, 0),
            uart.readWord(ret=[w.temp, w.status]),
            CMPI(w.status, 0),
            BNE(ll.exit),
            CMPI(w.temp, MAGIC),
            BNE(ll.bad_magic),
            uart.readWord(ret=[w.command, w.status]),
            CMPI(w.status, 0),
            BNE(ll.exit),
            uart.readWord(ret=[w.param1, w.status]),
            CMPI(w.status, 0),
            BNE(ll.exit),
            uart.readWord(ret=[w.param2, w.status]),
            CMPI(w.status, 0),
            BNE(ll.exit),
            uart.readWord(ret=[w.checksum, w.status]),
            CMPI(w.status, 0),
            BNE(ll.exit),
            Rem("Reset the CRC"),
            STXA(w.temp, self.reg.crc.reset),
            STXA(w.command, self.reg.crc.word),
            STXA(w.param1, self.reg.crc.word),
            STXA(w.param2, self.reg.crc.word),
            LDXA(w.temp, self.reg.crc.crc),
            CMPI(w.checksum, w.temp),
            BEQ(ll.exit),
            Rem("Bad Checksum"),
            MOVI(w.status, 3),
            J(ll.exit),
            ll("bad_magic"),
            MOVI(w.status, 2),
            ll("exit"),
        ]


class Transport:
    Send = SendPacket()
    Recv = RecievePacket()
    Hello = SendHelloResp()
