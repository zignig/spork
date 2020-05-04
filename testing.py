# minimal boot loader for the boneless

from boneless.arch.opcode import Instr
from boneless.arch.opcode import *

from ideal_spork.firmware.base import *

from uartIO import UART
from ideal_spork.firmware.stringer import Stringer
from console import Console

from ideal_spork.logger import logger

log = logger(__name__)


def Init(w, reg):
    return [
        Rem("Set up the devices"),
        # enable the led
        MOVI(w.temp, 1),
        STXA(w.temp, reg.statusled.en),
        # load the timer
        MOVI(w.temp, 0xFFFF),
        STXA(w.temp, reg.timer.reload_0),
        MOVI(w.temp, 0x00FF),
        STXA(w.temp, reg.timer.reload_1),
        # enable timer and events
        MOVI(w.temp, 1),
        STXA(w.temp, reg.timer.en),
        STXA(w.temp, reg.timer.ev.enable),
        # reset the crc
        MOVI(w.temp, 1),
        STXA(w.temp, reg.crc.reset),
        Rem("Move the start pointer into registers"),
        MOVR(w.address, "program_start"),
    ]


class Testing(Firmware):
    def setup(self):
        " registers in the bottom Window "
        self.w.req(["temp", "address", "checksum", "incoming_word", "status"])

    def prelude(self):
        " code before the main loop "
        return Init(self.w, self.reg)

    def instr(self):
        " Locals and the attached subroutine in the main loop "
        w = self.w
        reg = self.reg
        ll = LocalLabels()
        # create the subroutine
        uart = UART()
        # create a strings object
        strings = Stringer()
        strings.banner = "Looks like a firmware to me"
        strings.red = "\u001b[31m"
        strings.reset = "\u001b[0m"
        console = Console()
        return [
            # Write the greetings string
            strings.red(w.temp),
            uart.writestring(w.temp),
            strings.banner(w.temp),
            uart.writestring(w.temp),
            strings.reset(w.temp),
            uart.writestring(w.temp),
            # get the uart status
            ll("loop"),
            uart.read(ret=[w.incoming_word, w.status]),
            # if the status is zero skip
            CMPI(w.status, 0),
            BZ(ll.skip),
            # write the char back out
            uart.write(w.incoming_word),
            console.accept(w.incoming_word),
            ll("skip"),
            J(ll.loop),
        ]


if __name__ == "__main__":
    print("build test firmware")
    import fwtest

    spork = fwtest.build(Testing)
    spork.platform.build(spork, do_program=True)
