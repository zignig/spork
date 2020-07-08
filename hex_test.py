" Echo and Blink firmware"

from boneless.arch.opcode import Instr
from boneless.arch.opcode import *

from ideal_spork.firmware.base import *
from ideal_spork.firmware.firmware import Firmware

from uartIO import UART


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
            MOVI(w.endpoint, 1024),
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


class HexTest(Firmware):
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
            # Rem("print it out for now"),
            # ho(w.address),
            # MOVI(w.char, 58),  # colon
            # wc(w.char),
            # ho(w.value),
            # MOVI(w.char, 13),  # CR
            # wc(w.char),
            # MOVI(w.char, 10),  # LF
            # wc(w.char),
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
            J("init"),
            ll("err"),
            MOVI(w.char, 33),  # ! for error
            wc(w.char),
        ]


firmware = HexTest

if __name__ == "__main__":
    print("uploading bootloader")
    from upload import Uploader
    import fwtest

    spork = fwtest.build(firmware)
    up = Uploader()
    up.upload(spork, console=False)
