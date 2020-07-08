" Echo and Blink firmware"

from boneless.arch.opcode import Instr
from boneless.arch.opcode import *

from ideal_spork.firmware.base import *
from ideal_spork.firmware.firmware import Firmware

from uartIO import UART


class HexTest(Firmware):
    def setup(self):
        self.w.req(["value", "counter", "char", "input", "status"])

    def instr(self):
        serial = UART()
        reg = self.reg
        w = self.w
        ho = serial.writeHex
        wc = serial.write
        rh = serial.readHex
        ll = LocalLabels()
        return [
            ll("again"),
            rh(ret=[w.input, w.status]),
            CMPI(w.status, 1),  # error
            BEQ(ll.err),
            ho(w.input),
            MOVI(w.char, 13),  # CR
            wc(w.char),
            MOVI(w.char, 10),  # LF
            wc(w.char),
            J(ll.again),
            ll("err"),
            MOVI(w.char, 33),  # ! for error
            wc(w.char),
        ]
