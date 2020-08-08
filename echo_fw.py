#!/usr/bin/python
" Echo and Blink firmware"

from boneless.arch.opcode import Instr
from boneless.arch.opcode import *

from spork.firmware.base import *
from spork.firmware.firmware import Firmware

# Subroutine
class EchoChar(SubR):
    def setup(self):
        ...

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


class DeviceSetup(Inline):
    def instr(self, w):
        reg = self.reg
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

    # def prelude(self):
    #    return [DeviceSetup(self.w)()]

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


if __name__ == "__main__":
    print("build echo firmware")
    from upload import Uploader
    import fwtest

    spork = fwtest.build(Echo)
    up = Uploader()
    up.upload(spork)
