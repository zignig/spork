# minimal boot loader for the boneless

from boneless.arch.opcode import Instr
from boneless.arch.opcode import *

from ideal_spork.firmware.base import *

from uartIO import UART
from console import Console

from ideal_spork.firmware.stringer import Stringer

from ideal_spork.firmware.firmware import Firmware

from ideal_spork.logger import logger

log = logger(__name__)

"""
The structure of the bootloader goes something like this

THIS IS A LIE

wait for 2 magic words ( id ) 
wait for checksum
wait for length
copy words into memory and increment
check the checksum
boot into loaded program 

Refer to 

https://github.com/tpwrules/tasha_and_friends/blob/master/tasha/firmware/bootload.py
https://github.com/tpwrules/tasha_and_friends/blob/master/tasha/firmware/bootloader_fw.py

for inspiration

"""


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


class Bootloader(Firmware):
    LOADER_ID = "BL_0"

    requires = ["timer", "uart", "crc", "led"]

    def setup(self):
        " registers in the bottom Window "
        self.w.req(
            ["temp", "pad_address", "address", "checksum", "incoming_word", "status"]
        )

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
        # stringer global
        st = self.stringer
        st.loader_id = "\r\n" + self.LOADER_ID
        st.greetings = "MAY the spork be with you\r\n"
        st.warmboot = "Warmboot!"
        st.reset = "Reset!"
        st.prompt = "\r\n#>\r\n"

        console = Console()
        return [
            # Write the greetings string
            self.stringer.loader_id(w.temp),
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
            console(w.incoming_word, w.pad_address, ret=[w.status]),
            ll("skip"),
            J(ll.loop),
        ]


firmware = Bootloader

if __name__ == "__main__":
    print("uploading bootloader")
    from ideal_spork.utils.upload import Uploader
    import fwtest

    spork = fwtest.build(Bootloader)
    up = Uploader(spork, Bootloader)
    up.upload()
