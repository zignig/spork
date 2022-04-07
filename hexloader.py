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
serial = UART()
# short cuts to subroutines
ho = serial.writeHex
wc = serial.write
rh = serial.readHex


class ReadChunk(SubR):
    " read a chunk off the serial port into memory"
    params = ["address", "size"]
    locals = ["counter", "value"]
    ret = ["status"]

    def setup(self):
        pass

    def instr(self):
        ll = LocalLabels()
        w = self.w

        return [
            Rem("Load a chunk into memory"),
            ll("loop"),
            rh(ret=[w.value, w.status]),
            CMPI(w.status, 1),  # error
            BEQ(ll.err),
            ST(w.value, w.address, 0),
            ADDI(w.address, w.address, 1),
            SUBI(w.size, w.size, 1),
            CMPI(w.size, 0),
            BNE(ll.loop),
            ll("err"),
        ]


class CheckChunk(SubR):
    params = ["address", "size", "checksum"]
    locals = ["counter", "value"]
    ret = ["status"]

    def setup(self):
        pass

    def instr(self):
        w = self.w
        ll = LocalLabels()
        return [
            Rem("Check that a chunk is valid"),
            Rem("Reset the CRC"),
            STXA(w.value, self.reg.crc.reset),
            ll("checksum_loop"),
            Rem("get the value"),
            LD(w.value, w.address, 0),
            STXA(w.value, self.reg.crc.word),
            Rem("advance the counters"),
            ADDI(w.address, w.address, 1),
            SUBI(w.counter, w.counter, 1),
            CMPI(w.counter, 0),
            BNE(ll.checksum_loop),
            Rem("load the checksum value"),
            LDXA(w.value, self.reg.crc.crc),
            Rem("Compare the calculated CS with the bootloader value"),
            CMP(w.value, w.checksum),
            BNE(ll.check_fail),
            Rem("good value"),
            MOVI(w.status, 0),
            J(ll.out),
            ll("check_fail"),
            MOVI(w.status, 1),
            ll("out"),
        ]


class ProcessChunk(SubR):
    params = ["base_addr"]
    locals = ["value", "address", "size", "checksum"]
    ret = ["status"]

    def setup(self):
        pass

    def prelude(self):
        pass

    def instr(self):
        ll = LocalLabels()
        w = self.w
        read_chunk = ReadChunk()
        check_chunk = CheckChunk()
        return [
            Rem("load address (relative to base)"),
            rh(ret=[w.address, w.status]),
            CMPI(w.status, 1),  # error
            BEQ(ll.err),
            Rem("load the HEX count"),
            rh(ret=[w.size, w.status]),
            CMPI(w.status, 1),  # error
            BEQ(ll.err),
            Rem("load the checksum"),
            rh(ret=[w.checksum, w.status]),
            CMPI(w.status, 1),  # error
            BEQ(ll.err),
            Rem("Offset from base_addr"),
            ADD(w.address, w.address, w.base_addr),
            Rem("read the chunk into memory"),
            read_chunk(w.address, w.size, ret=[w.status]),
            CMPI(w.status, 1),
            BEQ(ll.err),
            Rem("check the check sum"),
            check_chunk(w.address, w.size, w.checksum, ret=[w.status]),
            CMPI(w.status, 1),
            BEQ(ll.err),
            ll("err"),
        ]


class LoaderAsSub(SubR):
    " have the bootloader as a subroutine so it can be added to other firmwares "
    params = ["address"]
    locals = ["value", "counter", "checksum", "status", "char"]

    def setup(self):
        pass

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

        proc_chunk = ProcessChunk()

        # make some ASM labels that will not collide.
        ll = LocalLabels()
        self.globals.counter = 0
        self.globals.boot_target = 0

        # return an array of instructions , this has a main loop wrapped around it
        return [
            # clean the registers, for a nice reset
            MOVI(R0, 0),
            MOVI(R1, 0),
            MOVI(R2, 0),
            MOVI(R3, 0),
            MOVI(R4, 0),
            MOVI(R5, 0),
            Rem("Get the count of chunks"),
            rh(ret=[w.counter, w.status]),
            CMPI(w.status, 1),  # error
            BEQ(ll.err),
            Rem("Stash the counter"),
            self.globals.counter(w.address),
            ST(w.counter, w.address, 0),
            Rem("Load the memory"),
            proc_chunk(w.address, ret=[w.status]),
            Rem("And boot into your newly minted firmware"),
            Rem("Clear the working registers"),
            # MOVR(w.address, "end_of_data"),
            MOVI(w.fp, self.sw - 8),
            STW(w.fp),
            MOVI(R0, 0),
            MOVI(R1, 0),
            MOVI(R2, 0),
            MOVI(R3, 0),
            MOVI(R4, 0),
            MOVI(R5, 0),
            J("end_of_data"),
            ll("check_fail"),
            MOVI(w.char, 70),  # F for checksum fail
            wc(w.char),
            J(ll.end),
            ll("err"),
            MOVI(w.char, 33),  # ! for error
            wc(w.char),
            Rem("any error will reset the bootloader"),
            ll("end"),
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

    def setup(self):
        # Define the registers used in this firmware "
        self.w.req(["value", "counter", "checksum", "address", "status", "char"])
        pass

    def instr(self):
        # TODO , make the target
        boot_as_sub = LoaderAsSub()
        self.globals.boot_target = 0
        w = self.w
        return [
            Rem("stash the target address"),
            Rem("so it can be used to load to other addresses"),
            self.globals.boot_target(w.address),
            MOVR(w.value, "end_of_data"),
            ST(w.value, w.address, 0),
            boot_as_sub(w.address),
        ]


firmware = HexLoader

if __name__ == "__main__":
    print("uploading bootloader")
    from spork.upload import Uploader
    import fwtest

    spork = fwtest.build(firmware, detail=False)
    up = Uploader()
    up.upload(spork, console=False, reset=False)
