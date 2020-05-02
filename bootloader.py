# minimal boot loader for the boneless


from boneless.arch.opcode import Instr
from boneless.arch.opcode import *

from ideal_spork.firmware.base import *

from uartIO import UART
from stringer import Stringer

from ideal_spork.logger import logger

log = logger(__name__)

"""
The structure of the bootloader goes something like this


wait for 2 magic words ( id ) 
wait for checksum
wait for length
copy words into memory and increment
check the checksum
boot into loaded program 

https://github.com/tpwrules/tasha_and_friends/blob/master/tasha/firmware/bootload.py
https://github.com/tpwrules/tasha_and_friends/blob/master/tasha/firmware/bootloader_fw.py


"""


def Init(w, reg):
    return [
        Rem("Set up the devices"),
        # enable the led
        MOVI(w.temp, 1),
        STXA(w.temp, reg.status_led_en),
        # load the timer
        MOVI(w.temp, 0xFFFF),
        STXA(w.temp, reg.timer_reload_0),
        MOVI(w.temp, 0x00FF),
        STXA(w.temp, reg.timer_reload_1),
        # enable timer and events
        MOVI(w.temp, 1),
        STXA(w.temp, reg.timer_en),
        STXA(w.temp, reg.timer_ev_enable),
        # reset the crc
        MOVI(w.temp, 1),
        STXA(w.temp, reg.crc_reset),
    ]


class Bootloader(Firmware):
    magic1 = 0xDEAD
    magic2 = 0xBEEF

    requires = ["timer", "uart", "crc", "led"]

    def instr(self):
        w = self.w
        reg = self.reg
        w.req(["temp", "address", "checksum", "incoming_word", "status"])
        ll = LocalLabels()
        # create the subroutine
        uart = UART()
        return [
            Init(w, reg),
            Rem("Move the start pointer into registers"),
            MOVR(w.address, "program_start"),
            ll("loop"),
            uart.read(ret=[w.incoming_word, w.status]),
            BZ(ll.skip),
            uart.write(w.incoming_word),
            ll("skip"),
            J(ll.loop),
            # uart.readword(ret=[w.incoming_word, w.status]),
            # CMPI(w.status, 0),
            # uart.writeword(w.incoming_word),
        ]


if __name__ == "__main__":
    print("uploading bootloader")
    from ideal_spork.utils.upload import Uploader

    up = Uploader(Bootloader)
    up.upload()
