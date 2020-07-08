" Echo and Blink firmware"

from boneless.arch.opcode import Instr
from boneless.arch.opcode import *

from ideal_spork.firmware.base import *
from ideal_spork.firmware.firmware import Firmware

from uartIO import UART


class HexTest(Firmware):
    def setup(self):
        self.w.req(["value", "counter", "char", "wait", "wait2"])

    def instr(self):
        serial = UART()
        reg = self.reg
        w = self.w
        ho = serial.writeHex
        wc = serial.write
        ll = LocalLabels()
        return [
            MOVI(w.counter, 0x00FA),
            ll("again"),
            ho(w.counter),
            MOVI(w.char, 13),  # CR
            wc(w.char),
            MOVI(w.char, 10),  # LF
            wc(w.char),
            ADDI(w.counter, w.counter, 1),
            MOVI(w.wait, 0xFFFF),
            MOVI(w.wait2, 0x4),
            ll("wait"),
            SUBI(w.wait, w.wait, 1),
            CMPI(w.wait, 0),
            BNE(ll.wait),
            SUBI(w.wait2, w.wait2, 1),
            CMPI(w.wait2, 0),
            BNE(ll.wait),
            J(ll.again),
        ]
