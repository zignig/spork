"Serail to word reading and writing"

from boneless.arch.opcode import Instr
from boneless.arch.opcode import *

from ideal_spork.firmware.base import *


class ReadWord(SubR):
    def setup(self):
        self.locals = ['counter','serial_flag','jump_save']
        self.ret = ['status','value']
        # 0 status is good
        # non zero is error

    def instr(self):
        timeout = 5000
        w = self.w
        reg = self.reg
        ll = LocalLabels()
        return [
            # load the timeout
            MOVI(w.counter,timeout),
            ll('wait'),
            # decrement the counter
            SUBI(w.counter,w.counter,1),
            # if zero jump to the timeout
            BZ(ll.timeout),
            LDXA(w.serial_flag,reg.serial_rx_rdy),
            CMPI(w.serial_flag,1),
            BEQ(ll.get_word),
            J(ll.wait),
            ll('timeout'),
            MOVI(w.status,1),
            Rem("return from the subroutine"), # this should be a macro
            ADJW(8),
            JR(R7, 0),
            ll('get_word'),
        ]
