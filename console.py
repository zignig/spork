"Console"

from boneless.arch.opcode import Instr
from boneless.arch.opcode import *

from ideal_spork.firmware.base import *


class CharPad(CodeObject):
    def __init__(self, name="CharPad", length=32):
        super().__init__()
        self.length = length
        self.name = name

    def __call__(self, register):
        self._used = True
        return [MOVR(register, self._prefix + self.name)]

    def code(self):
        data = [
            Rem("Data Pad"),
            L(self._prefix + self.name),
            Rem("length"),
            [self.length],
            Rem("pointer"),
            [0],
        ]
        data.extend([0] * self.length)
        return data


class Console:
    def __init__(self, pad):
        if not isinstance(pad, CharPad):
            raise FWError("Not a Pad")
        # Bind the pad into the function
        self.Accept.pad = pad
        # create the functions
        self.accept = self.Accept()

    class Accept(SubR):
        " Accept a char and put it into the pad"

        pad = None

        def setup(self):
            self.ret = ["value", "pad_address"]

        def instr(self):
            w = self.w
            reg = self.reg
            ll = LocalLabels()
            return [self.pad(R0), Rem("Not working yet")]


if __name__ == "__main__":
    c = CharPad()
    console = Console(c)

    def show():
        print(MetaSub.code())
        print(MetaObj.code())

    show()
