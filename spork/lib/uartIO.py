"Serail to char and word reading and writing"

from boneless.arch.opcode import Instr
from boneless.arch.opcode import *

from ..firmware.base import *


class ReadHex(SubR):
    " Read 4 hex char and make a 16 bit register"

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
    " Write a 16 bit reg as hex to the serial port"

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


class ReadWait(SubR):
    "Wait and return a char  "

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
    " Status and Char return "

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
    " Write a char to the uart"

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
            BEQ(ll.cont),
            J(ll.again),
            ll("cont"),
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


class WriteString(SubR):
    """ Write a string to the uart
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
    def setup(self):
        self.params = ["value"]
        self.locals = ["char", "status"]

    def instr(self):
        w = self.w
        reg = self.reg
        ll = LocalLabels()
        return [
            # get the lower char
            ANDI(w.char, w.value, 0xFF),
            # wait for the uart to be ready
            ll("wait"),
            LDXA(w.status, reg.serial_tx_rdy),
            CMPI(w.status, 1),
            BEQ(ll.cont),
            J(ll.wait),
            ll("cont"),
            STXA(w.char, reg.serial_tx_data),
            ll("wait2"),
            LDXA(w.status, reg.serial_tx_rdy),
            CMPI(w.status, 1),
            BEQ(ll.cont2),
            J(ll.wait2),
            ll("cont2"),
            SRLI(w.char, w.value, 8),
            STXA(w.char, reg.serial_tx_data),
        ]


class ReadWord(SubR):
    def setup(self):
        self.locals = ["counter", "char", "jump_save"]
        self.ret = ["status", "value"]
        # 0 status is good
        # non zero is error

    def instr(self):
        timeout = 0xFFFF
        w = self.w
        reg = self.reg
        ll = LocalLabels()
        return [
            # load zero into the value
            MOVI(w.value, 0),
            # wait for a char
            JAL(w.jump_save, ll.wait_char),
            # shift R by 8 bits
            SRLI(w.value, w.char, 8),
            # get another char
            JAL(w.jump_save, ll.wait_char),
            # char has the new value
            OR(w.value, w.value, w.char),
            MOVI(w.status, 0),
            ADJW(8),
            JR(w.ret, 0),
            # wait for char or timeout
            ll("wait_char"),
            # Load the timeout value
            MOVI(w.counter, timeout),
            ll("wait"),
            # decrement the counter
            SUBI(w.counter, w.counter, 1),
            # if zero jump to the timeout
            BZ(ll.timeout),
            # check if the serial port is ready
            LDXA(w.status, reg.serial_rx_rdy),
            CMPI(w.status, 1),
            BEQ(ll.get_char),
            J(ll.wait),
            # TIMEOUT
            ll("timeout"),
            MOVI(w.status, 1),
            Rem("return from the subroutine"),  # this should be a macro
            ADJW(8),
            JR(w.ret, 0),
            ll("get_char"),
            LDXA(w.char, reg.serial_rx_data),
            # insert into the crc engine
            STXA(w.char, reg.crc_byte),
            JR(w.jump_save, 0),
        ]


class CoreDump(SubR):
    " just dump the core "

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
            self.globals.heap(w.endpoint),
            LD(w.endpoint, w.endpoint, 0),
            ho(w.endpoint),
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
    readword = ReadWord()
    writeword = WriteWord()
    read = Read()
    write = Write()
    writestring = WriteString()
    writeHex = WriteHex()
    readHex = ReadHex()
    readWait = ReadWait()
    cr = CR()
    sp = SP()
    colon = COLON()
    core = CoreDump()
