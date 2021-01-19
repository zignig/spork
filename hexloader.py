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

# TODO
# print ID
# timeout (if there is another program)
# consume id
# calculate checksum


class LoaderAsSub(SubR):
    " have the bootloader as a subroutine so it can be added to other firmwares "

    locals = ["value", "counter", "checksum", "address", "status", "char"]

    def setup(self):
        pass

    def prelude(self):
        return [Rem("reset the CRC"), MOVI(w.temp, 1), STXA(w.temp, reg.crc.reset)]

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
        self.globals.counter = 0

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
            Rem("Stash the counter"),
            self.globals.counter(w.address),
            ST(w.counter, w.address, 0),
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
            Rem("Get the checksum"),
            rh(ret=[w.checksum, w.status]),
            CMPI(w.status, 1),  # error
            BEQ(ll.err),
            Rem("TODO, fix checksum"),
            STXA(w.address, self.reg.crc.reset),
            Rem("get the counter back"),
            self.globals.counter(w.address),
            LD(w.counter, w.address, 0),
            Rem("load the start of code"),
            MOVR(w.address, "end_of_data"),
            ll("checksum_loop"),
            Rem("get the value"),
            LD(w.value, w.address, 0),
            STXA(w.value, self.reg.crc.byte),
            Rem("shift for high byte"),
            NOP(0),
            SRLI(w.value, w.value, 8),
            STXA(w.value, self.reg.crc.byte),
            Rem("advance the counters"),
            ADDI(w.address, w.address, 1),
            SUBI(w.counter, w.counter, 1),
            CMPI(w.counter, 0),
            BNE(ll.checksum_loop),
            Rem("load the checksum value"),
            LDXA(w.value, self.reg.crc.crc),
            Rem("write out the checksum for now"),
            ho(w.value),
            Rem("And boot into your newly minted firmware"),
            Rem("Clear the working registers"),
            MOVR(w.address, "end_of_data"),
            MOVI(w.fp, self.sw - 8),
            STW(w.fp),
            MOVI(R0, 0),
            MOVI(R1, 0),
            MOVI(R2, 0),
            MOVI(R3, 0),
            MOVI(R4, 0),
            MOVI(R5, 0),
            J("end_of_data"),
            ll("err"),
            MOVI(w.char, 33),  # ! for error
            wc(w.char),
            Rem("any error will reset the bootloader"),
        ]


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
        # self.w.req(["value", "counter", "checksum", "address", "status", "char"])
        pass

    def instr(self):
        as_sub = LoaderAsSub()
        return [as_sub()]


firmware = HexLoader

if __name__ == "__main__":
    print("uploading bootloader")
    from spork.upload import Uploader
    import fwtest

    spork = fwtest.build(firmware, detail=False)
    up = Uploader()
    up.upload(spork, console=False, reset=False)
