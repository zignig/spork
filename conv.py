" Number Processing Functions"


from boneless.arch.opcode import Instr
from boneless.arch.opcode import *

from ideal_spork.firmware.base import *
from ideal_spork.firmware.stringer import Stringer
from uartIO import UART
from switch import Switch

from ideal_spork.logger import logger

log = logger(__name__)

from rich import print


class AsDec(SubR):
    " Convert a register into a decimal number"

    def setup(self):
        self.params = ["value", "target"]
        self.locals = ["holding", "leading", "index", "count"]

    def instr(self):
        """ Subtract from the the table set , until negative
        increment the count, move down the table until empty
        push digits onto the target"""

        w = self.w
        ll = LocalLabels()
        return [
            J(ll.table_end),  # jump past the data table
            ll("table_start"),
            10000,
            1000,
            100,
            10,
            1,
            ll("table_end"),
            MOVI(w.index, 0),
            MOVI(w.count, 0),
            MOV(w.holding, w.value),  # move into holding
            ll("again"),
        ]


class Numbers:
    dec = AsDec()


if __name__ == "__main__":
    d = AsDec()
    print(d.code())
