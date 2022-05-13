" Some Decimal Math functions  ; unfinished "

from boneless.arch.opcode import Instr
from boneless.arch.opcode import *

from ..firmware.base import *

from ..logger import logger

log = logger(__name__)

__done__ = False
__working__ = False


class DivMod(SubR):
    def setup(self):
        self.param = ["dividend", "divisor"]
        self.locals = ["count", "upper"]
        self.ret = ["quotient", "remainder"]

    def instr(self):
        w = self.w
        ll = LocalLabels()
        return [
            Rem("init"),
            Rem(" upper | dividend "),
            MOVI(w.counter, 16),
            MOVI(w.upper, 0),
            ll("divide"),
            Rem("Shift both left"),
            SLLI(w.dividend, 1),
            SLLI(w.upper, 1),
            Rem("Set bottom bit in upper"),
            BNS(ll.set_lower),
            ORI(w.upper, w.upper, 1),
            ll("set_lower"),
            Rem("Check that the divisor is positive"),
            SUB(w.remainder, w.upper, w.divisor),
            Rem("Is negative try again"),
            BNS(ll.skip),
            Rem("Positive, do stuff TODO"),
            ll("skip"),
            SUBI(w.counter, w.counter, 1),
            BZ(ll.exit),
            ll("exit"),
        ]


class PushDigit(SubR):
    "Push a digit onto the front of a string"

    def setup(self):
        self.params = ["spointer", "value"]
        self.locals = ["length", "index", "temp"]

    def instr(self):
        w = (self.w,)
        ll = LocalLabels()
        return [
            MOVI(w.index, 0),
            Rem("load the string length"),
            LD(w.length, w.spointer, 0),
            Rem("increase the length of the string"),
            ADDI(w.temp, w.length, 1),
            ST(w.temp, w.spointer, 0),
            Rem("Move to the end of the string"),
            ADD(w.spointer, w.spointer, w.length),
            ll("loop"),
            Rem("Load the value"),
            LD(w.temp, w.spointer, 0),
            Rem("Save it one to the right"),
            ST(w.temp, w.spointer, 1),
            Rem("Decrement pointer and index"),
            SUBI(w.spointer, w.spointer, 1),
            SUBI(w.length, w.length, 1),
            Rem("Last Char?"),
            CMPI(w.length, 1),
            BNZ(ll.loop),
            Rem("Store the Value, offset to 0 ascii"),
            ADDI(w.value, w.value, 48),
            ST(w.value, w.spointer, 0),
        ]


class Decimal(SubR):
    "Convert a Register to a decimal string"

    def setup(self):
        self.params = ["spointer", "value"]
        self.locals = ["digit", "base"]

    def instr(self):
        w = self.w
        ll = LocalLabels()
        pd = PushDigit()
        dm = DivMod()
        return [
            MOVI(w.base, 10),
            ll("again"),
            Rem("Divide By 10"),
            dm(w.value, w.base, ret=[w.value, w.digit]),
            Rem("Save the remainder digit"),
            pd(w.spointer, w.digit),
            Rem("Run out of digits?"),
            CMPI(w.value, 0),
            BNZ(ll.again),
        ]


if __name__ == "__main__":
    dm = DivMod()
    print(dm.code())
