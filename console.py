"Console"

from boneless.arch.opcode import Instr
from boneless.arch.opcode import *

from ideal_spork.firmware.base import *


class CharPad(CodeObject):
    def __init__(self, name="CharPad", length=32):
        super().__init__()
        self.length = length
        self._used = True  # just make it anyway
        self.name = name

    def __call__(self, register):
        self._used = True
        return [MOVR(register, self.name + self._postfix)]

    def code(self):
        data = [
            Rem("Data Pad"),
            L(self.name + self._postfix),
            Rem("length"),
            [self.length],
            Rem("pointer"),
            [0],
            Rem("pointer"),
            [0],
        ]
        data.extend([0] * self.length)
        return data


class Console:
    def __init__(self):
        # Bind the pad into the function
        # create the functions
        self.accept = self.Accept()

    class Accept(SubR):
        " Accept a char and put it into the pad"

        pad = CharPad()

        def setup(self):
            self.params = ["char"]
            self.ret = ["value", "pad_address"]

        def instr(self):
            w = self.w
            reg = self.reg
            ll = LocalLabels()
            return [self.pad(w.pad_address), Rem("Not working yet")]


if __name__ == "__main__":
    console = Console()
    SubR.reg = ""
    console.accept()
