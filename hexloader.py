" LOAD memory from a hex file "

from boneless.arch.opcode import Instr
from boneless.arch.opcode import *

# from allocator import *
# from boneless.arch.opcode import R0, R1, R2, R3, R4, R5, R6, R7, L

from spork.firmware.base import *
from spork.firmware import Firmware

from spork.lib.uartIO import UART

from spork.logger import logger

log = logger(__name__)


class HexLoader(Firmware):
    BOOTLOADER_ID = "BL_0"
    """
        This takes a CAPITAL hex string and loads it, and jumps to the first instruction
        
        Format is 16 bit 0000 - FFFF

        Length
        DATA
        CheckSum

    """

    log.critical("search for bootloader ID")

    def setup(self):
        # Define the registers used in this firmware "
        # TODO register allocator
        self.w.req(["value", "counter", "checksum", "address", "status", "char"])

    def instr(self):
        " instr returns an array of boneless instructions, make python things first "
        # the map of the IO registers
        reg = self.reg
        # the current register window
        w = self.w
        # make a collections of SubR , add only what you use
        serial = UART()
        # short cuts to subroutines
        ho = serial.writeHex
        wc = serial.write
        rh = serial.readHex
        # make some ASM labels that will not collide.
        ll = LocalLabels()

        # return an array of instructions , this has a main loop wrapped around it
        return [
            # clean the registers, for a nice reset
            MOVI(R0, 0),
            MOVI(R1, 0),
            MOVI(R2, 0),
            MOVI(R3, 0),
            MOVI(R4, 0),
            MOVI(R5, 0),
            Rem("Get the count of instructions"),
            rh(ret=[w.counter, w.status]),
            CMPI(w.status, 1),  # error
            BEQ(ll.err),
            Rem("Load the memory"),
            MOVR(w.address, "end_of_data"),
            ll("loop"),
            rh(ret=[w.value, w.status]),
            CMPI(w.status, 1),  # error
            BEQ(ll.err),
            ST(w.value, w.address, 0),
            ADDI(w.address, w.address, 1),
            SUBI(w.counter, w.counter, 1),
            CMPI(w.counter, 0),
            BNE(ll.loop),
            Rem("And boot into your newly minted firmware"),
            Rem("TODO, fix checksum"),
            Rem("Get the checksum"),
            rh(ret=[w.checksum, w.status]),
            CMPI(w.status, 1),  # error
            BEQ(ll.err),
            Rem("Clear the working registers"),
            MOVI(R0, 0),
            MOVI(R1, 0),
            MOVI(R2, 0),
            MOVI(R3, 0),
            MOVI(R4, 0),
            MOVI(R5, 0),
            MOVR(w.address, "end_of_data"),
            MOVI(w.fp, self.sw - 8),
            STW(w.fp),
            J("end_of_data"),
            ll("err"),
            MOVI(w.char, 33),  # ! for error
            wc(w.char),
            Rem("any error will reset the bootloader"),
        ]


firmware = HexLoader

if __name__ == "__main__":
    print("uploading bootloader")
    from spork.upload import Uploader
    import fwtest

    spork = fwtest.build(firmware, detail=False)
    up = Uploader()
    up.upload(spork, console=False, reset=False)
