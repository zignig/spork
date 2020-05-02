"Serail to char and word reading and writing"

from boneless.arch.opcode import Instr
from boneless.arch.opcode import *

from ideal_spork.firmware.base import *

class Read(SubR):
    " Status and Char return "
    def setup(self):
        self.ret = ["value","status"]
    def instr(self):
        w = self.w
        reg = self.reg
        ll = LocalLabels()
        return [ 
            Rem("Read a char of the serial port"),
            MOVI(w.status,0),
            #Get the serial port status 
            LDXA(w.status, reg.serial_rx_rdy),
            CMPI(w.status,0),
            BEQ(ll.skip), # skip if not ready
            # Load the char
            LDXA(w.value, reg.serial_rx_data),
            # Set the status to zero
            MOVI(w.status,1),
            ll('skip'),
        ]

class Write(SubR):
    def setup(self):
        self.params = ["value"]
        self.locals = ["status"]
    
    def instr(self):
        w = self.w
        reg = self.reg
        ll = LocalLabels()
        return [ 
            ll('again'), 
            LDXA(w.status,reg.serial_tx_rdy),
            CMPI(w.status,1),
            BEQ(ll.cont), 
            J(ll.again),
            ll('cont'),
            STXA(w.value, reg.serial_tx_data),
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


class UART:
    readword = ReadWord()
    writeword = WriteWord()
    read = Read()
    write = Write()
