# Spork templated file
# Created on Tue May 19 19:47:47 2020
" Echo and Blink firmware"

from boneless.arch.opcode import Instr
from boneless.arch.opcode import *

from ideal_spork.firmware.base import *

# Subroutine
class EchoChar(SubR):
    def instr(self):
        reg = self.reg
        return [
            # load the rx data
            LDXA(R3, reg.serial.rx.data),
            # send the byte to the crc engine
            STXA(R3, reg.crc.byte),
            # send the byte back out on the TX
            STXA(R3, reg.serial.tx.data),
        ]


# inline function
def Blink(w, reg):
    return [
        LDXA(w.temp, reg.timer.ev.pending),
        CMPI(w.temp, 1),
        # it has expired blink
        BNE("skip_blink"),
        MOVI(w.temp, 1),
        STXA(w.temp, reg.timer.ev.pending),
        # invert
        # write back to the leds
        STXA(w.leds, reg.statusled.led),
        XORI(w.leds, w.leds, 0xFFFF),
        L("skip_blink"),
    ]


def Init(w, reg):
    return [
        Rem("Enable the LED"),
        MOVI(w.temp, 1),
        STXA(w.temp, reg.statusled.en),
        Rem("Load the timer"),
        MOVI(w.temp, 0xFFFF),
        STXA(w.temp, reg.timer.reload_0),
        MOVI(w.temp, 0x00FF),
        STXA(w.temp, reg.timer.reload_1),
        Rem("Enable timer and events"),
        MOVI(w.temp, 1),
        STXA(w.temp, reg.timer.en),
        STXA(w.temp, reg.timer.ev.enable),
        Rem("Reset the CRC"),
        MOVI(w.temp, 1),
        STXA(w.temp, reg.crc.reset),
    ]


class Echo(Firmware):
    def setup(self):
        self.w.req(["leds", "temp"])

    def prelude(self):
        return [Init(self.w, self.reg)]

    def instr(self):
        echo_char = EchoChar()
        reg = self.reg
        w = self.w
        return [
            Rem("Blink the led on timer expire"),
            Blink(w, reg),
            Rem("Check if there is a char on the uart ?"),
            LDXA(w.temp, reg.serial.rx.rdy),
            CMPI(w.temp, 1),
            BNE("skip_echo"),
            echo_char(),
            L("skip_echo"),
        ]
