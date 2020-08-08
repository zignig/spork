#!/usr/bin/python
# minimal shell for the boneless

from boneless.arch.opcode import Instr
from boneless.arch.opcode import *

from spork.firmware.base import *

from spork.lib.uartIO import UART
from spork.lib.console import Console
from spork.lib.action import Action
from spork.lib.stringer import Stringer

from spork.firmware.firmware import Firmware

from spork.logger import logger

from spork.lib.commands import MetaCommand, Command

from spork.lib.banner import banner

import datetime

log = logger(__name__)

"""
An interactive console shell for the Boneless-v3 cpu"
"""


def Init(w, reg):
    return [
        Rem("Set up the devices"),
        Rem("enable the led"),
        MOVI(w.temp, 1),
        STXA(w.temp, reg.statusled.en),
        Rem("load the timer"),
        MOVI(w.temp, 0xFFFF),
        STXA(w.temp, reg.timer.reload_0),
        MOVI(w.temp, 0x00FF),
        STXA(w.temp, reg.timer.reload_1),
        Rem("enable timer and events"),
        MOVI(w.temp, 1),
        STXA(w.temp, reg.timer.en),
        STXA(w.temp, reg.timer.ev.enable),
        Rem("reset the crc"),
        MOVI(w.temp, 1),
        STXA(w.temp, reg.crc.reset),
        Rem("Move the start pointer into register for later jumpage"),
        MOVR(w.address, "program_start"),
    ]


class Bootloader(Firmware):
    LOADER_ID = "ZIG_0.0"

    # TODO check requirements
    requires = ["timer", "uart", "crc", "led"]

    def setup(self):
        " registers in the bottom Window "
        self.w.req(
            ["temp", "pad_address", "address", "checksum", "incoming_word", "status"]
        )

    def prelude(self):
        " code before the main loop "
        return Init(self.w, self.reg)

    def extra(self):
        "add in the commands"
        return MetaCommand.code()

    def instr(self):
        " Locals and the attached subroutine in the main loop "
        w = self.w
        reg = self.reg
        ll = LocalLabels()
        # create the subroutine
        uart = UART()
        List = MetaCommand.List()
        # stringer global
        st = self.stringer
        st.loader_id = "\r\n" + self.LOADER_ID
        st.greetings = "\r\nBoneless-CPU-v3\r\n"
        st.warmboot = "Warmboot!"
        st.reset = "Reset!"
        st.available = "Available Commands:"
        st.escape = "<ESC>"
        st.banner = banner.encode("utf-8")
        st.prompt = self.LOADER_ID + ">"
        st.date = str(datetime.datetime.now()) + "\r\n"

        console = Console()
        action = Action()

        return [
            # Write the prelude strings
            self.stringer.banner(w.temp),
            uart.writestring(w.temp),
            self.stringer.date(w.temp),
            uart.writestring(w.temp),
            self.stringer.greetings(w.temp),
            uart.writestring(w.temp),
            self.stringer.prompt(w.temp),
            uart.writestring(w.temp),
            # load the pad address into the register
            console.pad(w.pad_address),
            ll("loop"),
            # get the uart status
            uart.read(ret=[w.incoming_word, w.status]),
            # if the status is zero skip
            CMPI(w.status, 0),
            BZ(ll.skip),
            # write the char back out
            console(w.incoming_word, w.pad_address, w.status, ret=[w.status]),
            action(w.pad_address, w.status, ret=[w.status]),
            ll("skip"),
            J(ll.loop),
        ]


firmware = Bootloader

if __name__ == "__main__":
    from upload import Uploader
    import fwtest

    spork = fwtest.build(Bootloader, detail=False)
    up = Uploader()
    up.upload(spork)
