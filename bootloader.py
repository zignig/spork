# minimal boot loader for the boneless 


from boneless.arch.opcode import Instr
from boneless.arch.opcode import *

from ideal_spork.firmware.base import *

from uartIO import ReadWord

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

def Init(w,reg):
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
    def instr(self):
        w = self.w 
        reg = self.reg
        w.req(['temp','address','checksum','incoming_word','status'])
        # create the subroutine
        readword = ReadWord()
        return [ 
            Init(w,reg),
            Rem("Move the start pointer into registers"),
            MOVR(w.address,'program_start'),
            readword(ret=[w.incoming_word,w.status]),
 
        ]     
