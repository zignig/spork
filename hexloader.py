" LOAD memory from a hex file "

from boneless.arch.opcode import Instr
from boneless.arch.opcode import *


from spork.firmware.base import *
from spork.firmware import Firmware

from spork.lib.uartIO import UART
from spork.lib.stringer import Stringer
from spork.logger import logger

log = logger(__name__)

LOADER_ID = "BL3_"
# TODO
# print ID
# timeout (if there is another program)
# consume id
# calculate checksum
serial = UART()
# short cuts to subroutines
ho = serial.writeHex
wc = serial.write
rw = serial.readWait
rh = serial.readHex
nl = serial.cr
sp = serial.sp

stringer = Stringer(compact=False)
stringer.boot_id = LOADER_ID
# stringer.all()


class ZeroReg(Inline):
    def instr(self):
        return [
            Rem("Zero out the registers"),
            L("ZeroReg"),
            MOVI(R0, 0),
            MOVI(R1, 0),
            MOVI(R2, 0),
            MOVI(R3, 0),
            MOVI(R4, 0),
            MOVI(R5, 0),
            JR(R7, 0),
        ]


class GetNL(SubR):
    locals = ["value"]
    ret = ["status"]

    def instr(self):
        w = self.w
        ll = LocalLabels()
        return [
            rw(ret=[w.value]),
            CMPI(w.value, 13),
            BNE(ll.bad),
            MOVI(w.status, 0),
            J(ll.exit),
            ll("bad"),
            MOVI(w.status, 1),
            ll("exit"),
        ]


class ID(SubR):
    locals = ["address", "count", "value", "char"]
    ret = ["status"]

    def instr(self):
        w = self.w
        ll = LocalLabels()

        return [
            stringer.boot_id(w.address),
            LD(w.count, w.address, 0),
            Rem("advance to the first char"),
            ADDI(w.address, w.address, 1),
            ll("again"),
            LD(w.value, w.address, 0),
            rw(ret=[w.char]),
            CMP(w.value, w.char),
            BNE(ll.fail),
            Rem("advance the counters"),
            ADDI(w.address, w.address, 1),
            SUBI(w.count, w.count, 1),
            CMPI(w.count, 0),
            BNE(ll.again),
            MOVI(w.status, 0),
            J(ll.end),
            ll("fail"),
            MOVI(w.status, 1),
            ll("end"),
        ]


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
            # ho(w.value),
            ST(w.value, w.address, 0),
            ADDI(w.address, w.address, 1),
            SUBI(w.size, w.size, 1),
            CMPI(w.size, 0),
            BNE(ll.loop),
            ll("err"),
            # nl(),
        ]


class CheckChunk(SubR):
    params = ["address", "size", "checksum"]
    locals = ["value"]
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
            # ho(w.address),sp(),ho(w.value),nl(),
            Rem("advance the counters"),
            ADDI(w.address, w.address, 1),
            SUBI(w.size, w.size, 1),
            CMPI(w.size, 0),
            BNE(ll.checksum_loop),
            Rem("load the checksum value"),
            LDXA(w.value, self.reg.crc.crc),
            # nl(),
            # ho(w.checksum),
            # sp(),
            # ho(w.value),
            # nl(),
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
    params = ["base_addr", "size"]
    locals = ["value", "address", "checksum"]
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
            Rem("load the checksum"),
            rh(ret=[w.checksum, w.status]),
            CMPI(w.status, 1),  # error
            BEQ(ll.err),
            Rem("Offset from base_addr"),
            # ho(w.address),
            # serial.sp(),
            # ho(w.checksum),
            # serial.sp(),
            ADD(w.address, w.address, w.base_addr),
            Rem("read the chunk into memory"),
            read_chunk(w.address, w.size, ret=[w.status]),
            CMPI(w.status, 1),
            BEQ(ll.err),
            # nl(),
            Rem("check the check sum"),
            check_chunk(w.address, w.size, w.checksum, ret=[w.status]),
            # CMPI(w.status, 1),
            # BEQ(ll.err),
            ll("err"),
        ]


class LoaderAsSub(SubR):
    " have the bootloader as a subroutine so it can be added to other firmwares "
    params = ["address"]
    locals = ["value", "counter", "checksum", "status", "size"]

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
        wc = serial.writelongstring
        rh = serial.readHex
        gnl = GetNL()
        proc_chunk = ProcessChunk()
        id = ID()

        # make some ASM labels that will not collide.
        ll = LocalLabels()
        # self.globals.counter = 0
        # self.globals.boot_target = 0

        # return an array of instructions , this has a main loop wrapped around it
        return [
            # clean the registers, for a nice reset
            # JAL(R7,'ZeroReg'),
            Rem("Match the loader ID"),
            id(ret=[w.status]),
            CMPI(w.status, 1),
            BEQ(ll.id_fail),
            Rem("Get the count of chunks"),
            rh(ret=[w.counter, w.status]),
            CMPI(w.status, 1),  # error
            BEQ(ll.err),
            # ho(w.counter), # clean
            Rem("Get the size of each chunk"),
            rh(ret=[w.size, w.status]),
            CMPI(w.status, 1),  # error
            BEQ(ll.err),
            # ho(w.size),
            Rem("Load the memory"),
            ll("chunk_loop"),
            # ho(w.address),
            proc_chunk(w.address, w.size, ret=[w.status]),
            CMPI(w.status, 1),
            BEQ(ll.chunk_fail),
            # MOVI(w.status,89), # Y (YAY) for chunk
            # wc(w.status),
            SUBI(w.counter, w.counter, 1),
            CMPI(w.counter, 0),
            BNE(ll.chunk_loop),
            Rem("And boot into your newly minted firmware"),
            Rem("Clear the working registers"),
            MOVI(w.fp, self.sw - 8),
            STW(w.fp),
            # JAL(R7,'ZeroReg'),
            Rem("Jump into the program"),
            JR(w.address, 0),
            Rem("Error Sequences"),
            ll("id_fail"),
            # MOVI(w.size, 73),  # I
            stringer.boot_id(w.size),
            wc(w.size),
            ll("check_fail"),
            J(ll.end),
            MOVI(w.size, 70),  # F for checksum fail
            wc(w.size),
            J(ll.end),
            ll("chunk_fail"),
            MOVI(w.size, 67),  # ! for error
            wc(w.size),
            ho(w.counter),
            J(ll.end),
            ll("err"),
            MOVI(w.size, 33),  # ! for error
            # wc(w.size)
            J(ll.end),
            Rem("any error will reset the bootloader"),
            ll("end"),
        ]


class HexLoader(Firmware):
    BOOTLOADER_ID = "BL_0"
    """
        This takes a CAPITAL hex string and loads it, and jumps to the first instruction
        
        Format is 16 bit 0000 - FFFF

        BL3_
        chunk size
        chunk count
        newline 
        > list of chunks
        Relative address
        Checksum
        data , data , data , newline


    """

    def setup(self):
        # Define the registers used in this firmware "

        self.w.req(["value", "counter", "checksum", "address", "status", "char"])
        pass

    def extra(self):
        z = ZeroReg(self.w)
        return z()

    def instr(self):

        # TODO , make the target
        boot_as_sub = LoaderAsSub()
        w = self.w
        return [MOVR(w.address, "end_of_data"), boot_as_sub(w.address)]


firmware = HexLoader

if __name__ == "__main__":
    print("uploading bootloader")
    from spork.upload import Uploader
    import fwtest

    spork = fwtest.build(firmware, detail=False)
    up = Uploader()
    up.upload(spork, console=False, reset=False)
