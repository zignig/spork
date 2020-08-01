" LOAD memory from a hex file "

from boneless.arch.opcode import Instr
from boneless.arch.opcode import *

# from allocator import *
# from boneless.arch.opcode import R0, R1, R2, R3, R4, R5, R6, R7, L

from spork.firmware.base import *
from spork.firmware import Firmware

from spork.lib.uartIO import UART


class CoreDump(SubR):
    def setup(self):
        self.locals = ["counter", "endpoint", "char", "value"]

    def instr(self):
        w = self.w
        ll = LocalLabels()
        serial = UART()
        ho = serial.writeHex
        wc = serial.write
        return [
            Rem("DUMP the bootloader"),
            MOVI(w.counter, 0),
            MOVI(w.endpoint, 4096),
            ll("dumper"),
            Rem("current address"),
            # ho(w.counter),
            # MOVI(w.char, 32),  # SPACE
            # wc(w.char),
            LD(w.value, w.counter, 0),  # load the data from the address
            ho(w.value),
            # MOVI(w.char, 13),  # CR
            # wc(w.char),
            # MOVI(w.char, 10),  # LF
            # wc(w.char),
            ADDI(w.counter, w.counter, 1),  # increment the address
            CMP(w.counter, w.endpoint),
            BNE(ll.dumper),
        ]


class HexLoader(Firmware):
    def setup(self):
        self.w.req(["value", "counter", "checksum", "address", "status", "char"])

    def instr(self):
        serial = UART()
        reg = self.reg
        w = self.w
        ho = serial.writeHex
        wc = serial.write
        rh = serial.readHex
        ll = LocalLabels()
        cd = CoreDump()
        return [
            MOVI(R0, 0),
            MOVI(R1, 0),
            MOVI(R2, 0),
            MOVI(R3, 0),
            MOVI(R4, 0),
            MOVI(R5, 0),
            Rem("length word"),
            rh(ret=[w.counter, w.status]),
            CMPI(w.status, 1),  # error
            BEQ(ll.err),
            Rem("checksum word"),
            rh(ret=[w.checksum, w.status]),
            CMPI(w.status, 1),  # error
            BEQ(ll.err),
            Rem("Load the memory"),
            MOVR(w.address, "program_start"),
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
            MOVI(R0, 0),
            MOVI(R1, 0),
            MOVI(R2, 0),
            MOVI(R3, 0),
            MOVI(R4, 0),
            MOVI(R5, 0),
            MOVR(w.address, "program_start"),
            MOVI(w.fp, self.sw - 8),
            STW(w.fp),
            J("program_start"),
            ll("err"),
            MOVI(w.char, 33),  # ! for error
            wc(w.char),
        ]


firmware = HexLoader

if __name__ == "__main__":
    print("uploading bootloader")
    from upload import Uploader
    import fwtest

    spork = fwtest.build(firmware)
    # up = Uploader()
    # up.upload(spork, console=False)
