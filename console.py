"Console"

from boneless.arch.opcode import Instr
from boneless.arch.opcode import *

from ideal_spork.firmware.base import *
from ideal_spork.firmware.stringer import Stringer

from ideal_spork.logger import logger

from rich import print

log = logger(__name__)

""" Console and string handling functions
    for a shell interface 
    [ ] 
"""


class CharPad(CodeObject):
    """
        A character pad with console editing
    """

    def __init__(self, name="CharPad", length=32):
        super().__init__()
        self.length = length
        self.curser = length + 1
        self._used = True  # just make it anyway
        self.name = name

    def __call__(self, register):
        self._used = True
        return [MOVR(register, self.name + self._postfix)]

    def code(self):
        data = [Rem("Data Pad"), L(self.name + self._postfix), Rem("length")]
        data.extend([0] * self.length)
        data += [Rem("length"), [self.length], Rem("cursor"), [0]]
        return data


class Switch:
    " Construct a jump table for single chars, or integers "

    def __init__(self, window, select, default=None):
        self.mapping = {}
        self.labels = LocalLabels()
        self.window = window
        self.select = select  # a register in window
        window.req(["jumpval"])

    def add(self, item):
        if len(item) != 2:
            raise FWError()
        if isinstance(item, list):
            for i in item:
                self.add(i, item)
        val = item[0]
        subroutine = item[1]
        # insert the mapping
        if isinstance(val, str):
            val = ord(val)
            self.mapping[val] = subroutine
        elif isinstance(val, int):
            self.mapping[val] = subroutine

    def dump(self):
        ll = self.labels
        w = self.window
        data = [Rem("start of the jump table")]
        # map the values
        for i, j in enumerate(self.mapping):
            log.critical("{:d} -> {:d} -> {:s}".format(i, j, str(self.mapping[j])))
            data += [
                Rem("start-" + str(j)),
                [
                    MOVI(w.jumpval, j),
                    CMP(w.jumpval, self.select),
                    BZ("{:04d}{:s}".format(i, ll._postfix)),
                    Rem("end-" + str(j)),
                ],
            ]
        data += [Rem("end of jump table")]
        for i, j in enumerate(self.mapping):
            log.critical(
                "trace {:d} -> {:d} -> {:s}".format(i, j, str(self.mapping[j]))
            )
            data += [ll("{:04d}".format(i))]
            data += [self.mapping[j], J(ll.table_end)]
        data += [ll("table_end")]
        return data


class Console(SubR):
    def setup(self):
        param = []
        local = []
        ret = ["status"]
        # Bind the pad into the function
        # create the functions
        self.accept = self.Accept()
        self.pad = CharPad()
        self.w.req("choice")
        self.selector = sel = Switch(self.w, self.w.choice)
        # char selector

    class Accept(SubR):
        " Accept a char and put it into the pad"

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
    w = Window()
    w.req("val")
    s = Stringer()
    ll = LocalLabels()
    s.test = "this is a test"
    w.req(["pad", "value"])
    cs = Switch(w, w.val)
    cs.add(("c", [ll("a")]))
    cs.add(("r", [ll("b")]))
    cs.add(("s", [ll("c")]))
    cs.add((43, [ll("d")]))
    cs.add((10, [ll("e")]))
    cs.add((13, [ll("f")]))
    d = cs.dump()
    print(d)
    r = Instr.assemble(d)
    d = Instr.disassemble(r)
    print(r)
    print(d)
