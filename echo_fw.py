
from boneless.arch.opcode import Instr
from boneless.arch.opcode import *

from ideal_spork.firmware.base import *

# Subroutine
class EchoChar(SubR):
    def instr(self):
        reg = self.reg
        return [
            # load the rx data
            LDXA(R3, reg.serial_rx_data),
            # send the byte to the crc engine
            STXA(R3, reg.crc_byte),
            # send the byte back out on the TX
            STXA(R3, reg.serial_tx_data),
        ]


# inline function
def Blink(w,reg):
    return [
        LDXA(w.temp, reg.timer_ev_pending),
        CMPI(w.temp, 1),
        # it has expired blink
        BNE("skip_blink"),
        MOVI(w.temp, 1),
        STXA(w.temp, reg.timer_ev_pending),
        # invert
        # write back to the leds
        STXA(w.leds, reg.status_led_led),
        XORI(w.leds, w.leds, 0xFFFF),
        L("skip_blink"),
    ]


def Init(w,reg):
    return [
        MOVI(w.temp, 1),
        STXA(w.temp, reg.status_led_en),
        #STXA(w.temp, reg.status_led_led),
        # load the timer
        MOVI(w.temp, 0xFFF),
        STXA(w.temp, reg.timer_reload),
        # enable timer and events
        MOVI(w.temp, 1),
        STXA(w.temp, reg.timer_en),
        STXA(w.temp, reg.timer_ev_enable),
        # reset the crc
        MOVI(w.temp, 1),
        STXA(w.temp, reg.crc_reset),
    ]


class Echo(Firmware):
    def instr(self):
        echo_char = EchoChar()
        reg = self.reg
        w = self.w
        w.req("leds")
        w.req("temp")
        return [
            Init(w,reg),
            L("main_loop"),
            Blink(w,reg),
            # is there a char on the uart ?
            LDXA(w.temp, reg.serial_rx_rdy),
            CMPI(w.temp, 1),
            BNE("skip_echo"),
            echo_char(),
            L("skip_echo"),
            J("main_loop"),
        ]
