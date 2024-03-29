"""
    Serial to char and word reading and writing
    
    UART functions for various data forms
"""

from boneless.arch.opcode import Instr
from boneless.arch.opcode import *

from ..firmware.base import *


class ReadHex(SubR):
    "Read 4 hex char and make a 16 bit register"

    def setup(self):
        self.ret = ["value", "status"]
        self.locals = ["temp", "nibble", "char", "repeat"]

    def instr(self):
        w = self.w
        reg = self.reg
        ll = LocalLabels()
        readw = ReadWait()
        wr = Write()
        return [
            Rem("Read hex register off serial port"),
            MOVI(w.status, 0),
            MOVI(w.value, 0),
            MOVI(w.repeat, 4),
            ll("again"),
            readw(ret=w.char),  # wait for a char
            Rem("convert char to value"),
            CMPI(w.char, 48),  # 0 char
            BLTU(ll.err),  # out of hex range
            CMPI(w.char, 57),  # 9 char
            BGTU(ll.letter),  # above the 9 , could be a letter
            SUBI(w.char, w.char, 48),  # make the number
            J(ll.cont),  # continue
            ll("letter"),
            CMPI(w.char, 70),  # compare with F
            BGTU(ll.err),  # hex out of range
            CMPI(w.char, 65),  # compare with A
            BLTU(ll.err),  # in the gap 0 - A
            SUBI(w.char, w.char, 55),  # make the number A - (10)
            ll("cont"),
            Rem("at this point the w.char register should be a number 0-15"),
            SLLI(w.value, w.value, 4),  # rotate the nibble to the left.
            OR(w.value, w.value, w.char),  # insert the nibble into the value
            SUBI(w.repeat, w.repeat, 1),  # decrement the counter
            CMPI(w.repeat, 0),  # check the counter
            BNE(ll.again),
            # Set the status to 0
            MOVI(w.status, 0),
            J(ll.out),
            ll("err"),
            # Set the status to 1
            MOVI(w.status, 1),
            ll("out"),
        ]


class WriteHex(SubR):
    "Write a 16 bit reg as hex to the serial port"

    def setup(self):
        self.params = ["value"]
        self.locals = ["temp", "nibble", "char", "repeat"]

    def instr(self):
        w = self.w
        reg = self.reg
        ll = LocalLabels()
        wr = Write()
        return [
            MOVI(w.repeat, 4),
            AND(w.temp, w.value, w.value),  # copy to temp
            ll("again"),
            ROLI(w.temp, w.temp, 4),
            AND(w.nibble, w.temp, w.temp),
            ANDI(w.nibble, w.nibble, 15),  # get the first 4 bits
            AND(w.char, w.nibble, w.nibble),  # copy to temp
            Rem("convert to char"),
            CMPI(w.char, 10),
            BGEU(ll.letter),
            ADDI(w.char, w.char, 48),  # number
            J(ll.write),
            ll("letter"),
            ADDI(w.char, w.char, 55),  # letter
            ll("write"),
            wr(w.char),  # write it to the uart
            SUBI(w.repeat, w.repeat, 1),  # decrement the counter
            CMPI(w.repeat, 0),  # check the counter
            BNE(ll.again),
        ]


class WriteBin(SubR):
    "Write a 16 bit reg as binary to the serial port"

    def setup(self):
        self.params = ["value"]
        self.locals = ["temp", "char", "repeat"]

    def instr(self):
        w = self.w
        reg = self.reg
        ll = LocalLabels()
        wr = Write()
        return [
            MOVI(w.repeat, 16),
            AND(w.temp, w.value, w.value),  # copy to temp
            ll("again"),
            CMPI(w.temp, 0xFFFF),
            BS(ll.one),
            MOVI(w.char, 48),  # zero
            wr(w.char),
            J(ll.next),
            ll("one"),
            MOVI(w.char, 49),  # one
            wr(w.char),
            ll("next"),
            SLLI(w.temp, w.temp, 1),
            SUBI(w.repeat, w.repeat, 1),  # decrement the counter
            CMPI(w.repeat, 0),  # check the counter
            BNE(ll.again),
        ]


class ReadWait(SubR):
    "Wait and return a char"

    def setup(self):
        self.ret = ["value"]
        self.locals = ["status"]

    def instr(self):
        w = self.w
        reg = self.reg
        ll = LocalLabels()
        return [
            Rem("Wait and read a char off the serial port"),
            MOVI(w.status, 0),
            # Get the serial port status
            ll("wait"),
            LDXA(w.status, reg.serial.rx.rdy),
            CMPI(w.status, 0),
            BEQ(ll.wait),  # wait if not ready
            # Load the char
            LDXA(w.value, reg.serial.rx.data),
        ]


class Read(SubR):
    "Status and Char return"

    def setup(self):
        self.ret = ["value", "status"]

    def instr(self):
        w = self.w
        reg = self.reg
        ll = LocalLabels()
        return [
            Rem("Read a char off the serial port"),
            MOVI(w.status, 0),
            # Get the serial port status
            LDXA(w.status, reg.serial.rx.rdy),
            CMPI(w.status, 0),
            BEQ(ll.skip),  # skip if not ready
            # Load the char
            LDXA(w.value, reg.serial.rx.data),
            # Set the status to one
            MOVI(w.status, 1),
            ll("skip"),
        ]


class Write(SubR):
    "Write a char to the uart"

    def setup(self):
        self.params = ["value"]
        self.locals = ["status"]

    def instr(self):
        w = self.w
        reg = self.reg
        ll = LocalLabels()
        return [
            Rem("Make sure the uart is ready"),
            ll("again"),
            LDXA(w.status, reg.serial.tx.rdy),
            CMPI(w.status, 1),
            BNE(ll.again),
            STXA(w.value, reg.serial.tx.data),
        ]


class CR(SubR):
    def setup(self):
        self.locals = ["char"]

    def instr(self):
        w = self.w
        wc = Write()
        return [MOVI(w.char, 13), wc(w.char), MOVI(w.char, 10), wc(w.char)]  # CR  # LF


class COLON(SubR):
    def setup(self):
        self.locals = ["char"]

    def instr(self):
        w = self.w
        wc = Write()
        return [MOVI(w.char, 58), wc(w.char)]  # SPACE


class SP(SubR):
    def setup(self):
        self.locals = ["char"]

    def instr(self):
        w = self.w
        wc = Write()
        return [MOVI(w.char, 32), wc(w.char)]  # SPACE


class WriteLongString(SubR):
    """Only write long strings no compact check"""

    def setup(self):
        self.params = ["address"]
        self.locals = ["length", "value"]

    def instr(self):
        w = self.w
        reg = self.reg
        ll = LocalLabels()
        # create the subroutine
        uart_out = Write()
        return [
            LD(w.length, w.address, 0),
            ADDI(w.address, w.address, 1),
            ll("loop"),
            # Write out the char
            LD(w.value, w.address, 0),
            uart_out(w.value),
            # Increment the address
            ADDI(w.address, w.address, 1),
            # Increment the counter
            SUBI(w.length, w.length, 1),
            # check if we are at length
            CMPI(w.length, 0),
            BNE(ll.loop),
        ]


class WriteString(SubR):
    """Write a string to the uart
    Strings are pascal style with the length as the first word
    """

    def setup(self):
        self.params = ["address"]
        self.locals = ["length", "counter", "value", "char"]

    def instr(self):
        w = self.w
        reg = self.reg
        ll = LocalLabels()
        # create the subroutine
        uart_out = Write()
        return [
            # Value is the address of the string
            # Load the length of the string
            Rem("empty string bail"),
            LD(w.length, w.address, 0),
            CMPI(w.length, 0),
            BEQ(ll.exit),
            # Increment the address so it is at the start of the data
            ADDI(w.address, w.address, 1),
            # Reset the counter
            MOVI(w.counter, 0),
            Rem("Check if it is a compact string"),
            Rem("sign bit is set?"),
            CMPI(w.length, 0),
            BNS(ll.lf_loop),
            Rem("Set high bit to zero"),
            ANDI(w.length, w.length, 0x8000 - 1),
            Rem("Compact Strings"),
            Rem("strings are byte encoded"),
            ll("cf_loop"),
            LD(w.value, w.address, 0),
            Rem("first char"),
            SRLI(w.char, w.value, 8),
            uart_out(w.char),
            ADDI(w.counter, w.counter, 1),
            CMP(w.length, w.counter),
            BEQ(ll.exit),
            Rem("second char"),
            ANDI(w.char, w.value, 0xFF),
            uart_out(w.char),
            ADDI(w.counter, w.counter, 1),
            ADDI(w.address, w.address, 1),
            CMP(w.length, w.counter),
            BEQ(ll.exit),
            J(ll.cf_loop),
            Rem("Long form strings"),
            ll("lf_loop"),
            # Write out the char
            LD(w.value, w.address, 0),
            uart_out(w.value),
            # Increment the address
            ADDI(w.address, w.address, 1),
            # Increment the counter
            ADDI(w.counter, w.counter, 1),
            # check if we are at length
            CMP(w.length, w.counter),
            BEQ(ll.exit),
            J(ll.lf_loop),
            ll("exit"),
        ]


class WriteWord(SubR):

    params = ["value"]
    locals = ["char", "counter", "timeout"]
    ret = ["status"]

    def instr(self):
        w = self.w
        reg = self.reg
        ll = LocalLabels()
        return [
            # get the upper byte
            SRLI(w.char, w.value, 8),
            # wait for the uart to be ready
            ll("wait"),
            LDXA(w.status, reg.serial.tx.rdy),
            CMPI(w.status, 1),
            BNE(ll.wait),
            STXA(w.char, reg.serial.tx.data),
            ll("wait2"),
            LDXA(w.status, reg.serial.tx.rdy),
            CMPI(w.status, 1),
            BNE(ll.wait2),
            # get the lower byte
            ANDI(w.char, w.value, 0xFF),
            STXA(w.char, reg.serial.tx.data),
        ]


class ReadWord(SubR):
    def setup(self):
        self.locals = ["counter", "char", "timeout"]
        self.ret = ["value", "status"]
        # 0 status is good
        # non zero is error

    def instr(self):
        timeout = 0xFFFF
        w = self.w
        reg = self.reg
        ll = LocalLabels()
        return [
            MOVI(w.counter, 0),
            MOVI(w.status, 0),
            MOVI(w.value, 0),
            Rem("First Char"),
            [
                ll("wait"),
                LDXA(w.status, reg.serial.rx.rdy),
                CMPI(w.status, 0),
                BNE(ll.cont),
                ADDI(w.counter, w.counter, 1),
                CMPI(w.counter, timeout),
                BEQ(ll.timeout),
                J(ll.wait),
            ],
            ll("cont"),
            LDXA(w.char, reg.serial.rx.data),
            SLLI(w.value, w.char, 8),
            Rem("Second Char"),
            MOVI(w.counter, 0),
            [
                ll("wait2"),
                LDXA(w.status, reg.serial.rx.rdy),
                CMPI(w.status, 0),
                BNE(ll.cont2),
                ADDI(w.counter, w.counter, 1),
                CMPI(w.counter, timeout),
                BEQ(ll.timeout),
                J(ll.wait2),
            ],
            ll("cont2"),
            LDXA(w.char, reg.serial.rx.data),
            OR(w.value, w.value, w.char),
            MOVI(w.status, 0),
            J(ll.exit),
            ll("timeout"),
            MOVI(w.status, 2),
            ll("exit"),
        ]


class CoreDump(SubR):
    "just dump the core"

    def setup(self):
        self.locals = ["counter", "endpoint", "char", "value", "slice"]

    def instr(self):
        w = self.w
        ll = LocalLabels()
        uart = UART()
        ho = uart.writeHex
        wc = uart.write
        return [
            Rem("DUMP the entire memory space"),
            MOVI(w.counter, 0),
            self.globals.heap_pointer(w.endpoint),
            LD(w.endpoint, w.endpoint, 0),
            # MOVR(w.endpoint, "end_of_data"),  # TODO share full mem size into SubR
            ll("dumper"),
            Rem("current address"),
            LD(w.value, w.counter, 0),  # load the data from the address
            # ho(w.value),
            # uart.sp(),
            Rem("every 32 words make a line break"),
            ANDI(w.slice, w.counter, 0x1F),
            # ANDI(w.slice, w.counter, 0x0F),
            # ho(w.slice),
            # uart.cr(),
            CMPI(w.slice, 0),
            BNE(ll.cont),
            uart.cr(),
            ho(w.counter),
            uart.sp(),
            uart.colon(),
            uart.sp(),
            ll("cont"),
            ho(w.value),
            uart.sp(),
            ADDI(w.counter, w.counter, 1),  # increment the address
            CMP(w.counter, w.endpoint),
            BNE(ll.dumper),
        ]


class UART:
    readWord = ReadWord()
    writeWord = WriteWord()
    read = Read()
    write = Write()
    writestring = WriteString()
    writelongstring = WriteLongString()
    writeHex = WriteHex()
    writeBin = WriteBin()
    readHex = ReadHex()
    readWait = ReadWait()
    cr = CR()
    sp = SP()
    colon = COLON()
    core = CoreDump()
