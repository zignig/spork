#!/usr/bin/python
# minimal shell for the boneless

# the instruction set
# TODO port to allocator IR
from boneless.arch.opcode import Instr
from boneless.arch.opcode import *

# the firmare constructs
from spork.firmware.base import *

# the library code
from spork.lib.uartIO import UART
from spork.lib.console import Console
from spork.lib.action import Action, dumpEsc
from spork.lib.stringer import Stringer
from spork.lib.ansi_codes import AnsiStrings, Term
from spork.firmware.firmware import Firmware

from spork.lib.alloc import Alloc

# command infrastructure
from spork.lib.commands import MetaCommand, Command

# these automatically get added to the firmware
import spork.lib.base_command

# TODO compress the banner, it is phat.
from spork.lib.banner import banner

# date stamp
import datetime

from spork.logger import logger

log = logger(__name__)


"""
An interactive console shell for the Boneless-v3 cpu"
"""

# TODO convert to inline
class Init(Inline):
    " Run this code on reset , device init "
    # TODO find best way to attach this to the peripherals.
    def instr(self):
        w = self.w
        reg = self.reg
        self.globals.heap = 0
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
            Rem("Reset the heap"),
            self.globals.heap(w.temp),
            MOVR(w.pad_address, "end_of_data"),
            ST(w.pad_address, w.temp, 0),
            MOVI(w.temp, 32),
        ]


# A subclass of Command will add the name into the command line search list
# TODO limit the auto insert.
class show(Command):
    " List the escape code Enumerator names"

    class _show(SubR):
        def setup(self):
            self.locals = ["temp"]
            # mark the SubR so it is included without
            # being called
            # IF you don't mark it , the code will not be included.
            self.mark()

        def instr(self):
            # show the escape stings.
            s = dumpEsc()
            return [s()]

    # Bind the subroutine to the code
    call = _show()


class al(Command):
    " allocation testing "

    class _al_test(SubR):
        def setup(self):
            self.locals = ["temp"]
            # mark the SubR so it is included without
            # being called
            self.mark()

        def instr(self):
            w = self.w
            al = Alloc()
            u = UART()
            ho = u.writeHex
            return [
                MOVI(w.temp, 512),
                al(w.temp),
                self.globals.heap(w.temp),
                LD(w.temp, w.temp, 0),
                ho(w.temp),
            ]

    # Bind the subroutine to the code
    call = _al_test()


class ON(Command):
    " switch on the led "

    class _ledon(SubR):
        def setup(self):
            self.locals = ["temp"]
            # mark the SubR so it is included without
            # being called
            self.mark()

        def instr(self):
            w = self.w
            return [MOVI(w.temp, 1), STXA(w.temp, self.reg.statusled.led)]

    # Bind the subroutine to the code
    call = _ledon()


class OFF(Command):
    " switch off the led "

    class _ledoff(SubR):
        def setup(self):
            self.locals = ["temp"]
            self.mark()

        def instr(self):
            w = self.w
            return [MOVI(w.temp, 0), STXA(w.temp, self.reg.statusled.led)]

    call = _ledoff()


class Bootloader(Firmware):
    LOADER_ID = "ZIG_0"

    # TODO check requirements
    requires = ["timer", "uart", "crc", "led"]

    def setup(self):
        " registers in the bottom Window "
        self.w.req(
            ["temp", "pad_address", "address", "checksum", "incoming_word", "status"]
        )

    def prelude(self):
        " code before the main loop "
        i = Init(self.w)
        return i()

    # this code is in spork/firmware/base.py
    def extra(self):
        "add in the commands"
        return MetaCommand.code()

    # Code objects need to return a list of ASM instructions to do stuff.
    def instr(self):
        " Locals and the attached subroutine in the main loop "
        " my window "
        w = self.w
        " my registers "
        reg = self.reg
        " make some label that are local"
        ll = LocalLabels()
        # create the subroutines
        """ 
        by making the the SubR are available , if they are called 
        if they are used they will be added to the firmware.
        """
        uart = UART()
        List = MetaCommand.List()
        " global strings, if they are used they are added"
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
        st.date = str(datetime.datetime.today()) + "\r\n"
        st.backspace = "<BS>"

        " load the ansi codes that are used "
        AnsiStrings(st)
        " make a terminal code object "
        term = Term()

        " some global _fixed_ references "
        self.globals.led = 0
        self.globals.cursor = 0
        # TODO make globals typesafe

        " build some data and subroutines "
        console = Console()
        action = Action()

        " list of instructions to run "
        " main loop "
        return [
            Rem("Write the prelude strings"),
            Rem("Banner"),
            # self.stringer.banner(w.temp),
            ##uart.writestring(w.temp),
            Rem("Time Stamp"),
            self.stringer.date(w.temp),
            uart.writestring(w.temp),
            Rem("Hello"),
            self.stringer.greetings(w.temp),
            uart.writestring(w.temp),
            uart.cr(),
            Rem("Write the prompt"),
            self.stringer.prompt(w.temp),
            uart.writestring(w.temp),
            Rem("load the pad address into the register"),
            # console.pad(w.pad_address),
            ll("loop"),
            Rem("get the uart status"),
            uart.read(ret=[w.incoming_word, w.status]),
            Rem("if the status is zero skip"),
            CMPI(w.status, 0),
            BZ(ll.skip),
            Rem("process the keystroke"),
            console(w.incoming_word, w.pad_address, w.status, ret=[w.status]),
            action(w.pad_address, w.status, ret=[w.status]),
            ll("skip"),
            J(ll.loop),
        ]


" load this "
firmware = Bootloader

if __name__ == "__main__":
    from spork.upload import Uploader
    import fwtest

    spork = fwtest.build(Bootloader, detail=False)
    up = Uploader()
    up.upload(spork)
