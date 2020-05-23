"Console"

from boneless.arch.opcode import Instr
from boneless.arch.opcode import *

from ideal_spork.firmware.base import *
from ideal_spork.firmware.stringer import Stringer
from uartIO import UART
from warm import WarmBoot

from ideal_spork.logger import logger

log = logger(__name__)

from rich import print


""" Console and string handling functions
    for a shell interface 
    [X] reset
    [X] warmboot
    [ ] echo
"""


class CharPad(CodeObject):
    """
        A character pad with console editing
    """

    # Add functions for the Char pad here
    class Accept(SubR):
        def setup(self):
            self.params = ["pad_address", "char"]
            self.locals = ["length"]

        def instr(self):
            return []

    def __init__(self, name="CharPad", length=32):
        super().__init__()
        self.length = length
        self.total_length = length + 1
        self.cursor = length + 2
        self._used = False  # just make it anyway
        self.name = name
        # Some internal functions
        self.accept = self.Accept()

    def __call__(self, register):
        self._used = True
        return [MOVR(register, self.name + self._postfix)]

    def code(self):
        data = [Rem("Data Pad"), L(self.name + self._postfix), Rem("length")]
        data.extend([0] * self.length)
        data += [Rem("total_length"), [self.length], Rem("cursor"), [0]]
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

    def __call__(self):
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
        data += [J(ll.table_end), Rem("end of jump table")]
        for i, j in enumerate(self.mapping):
            log.critical(
                "trace {:d} -> {:d} -> {:s}".format(i, j, str(self.mapping[j]))
            )
            data += [ll("{:04d}".format(i))]
            data += [self.mapping[j], J(ll.table_end)]
        data += [ll("table_end")]
        return data


class Console(SubR):
    # Subroutines inside the console

    class Enter(SubR):
        " just write the pad back to the serial port for now"

        def setup(self):
            self.params = ["pad_address"]
            self.locals = ["temp"]
            self.uart = UART()

        def instr(self):
            w = self.w
            return [
                UART.writestring(w.pad_address),
                MOVI(w.temp, 0),
                Rem("clear the length"),
                ST(w.pad_address, w.temp, 0),
                Rem("clear the cursor"),
                ST(w.pad_address, w.temp, 64),
            ]

    class Char(Inline):
        " Echo and accept echoable chars"
        log.critical("Accept printable char")
        pass

    def setup(self):
        self.params = ["char", "pad_address"]
        self.locals = ["temp"]
        self.ret = ["status"]

    def build(self):
        # Bind the pad into the function
        self.pad = CharPad()

        # self.char = self.Char(self.w)

        self.selector = sel = Switch(self.w, self.w.char)
        ll = LocalLabels()
        enter = self.Enter()
        st = Stringer()
        st.back = "\n>"
        uart = UART()
        wb = WarmBoot()
        # CR does prompt for now
        sel.add((13, [st.back(self.w.temp), uart.writestring(self.w.temp)]))
        sel.add((10, [st.back(self.w.temp), uart.writestring(self.w.temp)]))
        # ^C Restart , warm boot
        sel.add((4, [Rem("^D Restart"), MOVI(self.w.temp, 1), wb(self.w.temp)]))
        # ^D Init the firmware
        sel.add((3, [Rem("^C Init processor"), J("init")]))
        # TAB complete
        sel.add((3, [Rem("^C Init processor"), J("init")]))
        # ESCAPE
        sel.add((3, [Rem("^C Escape"), J("init")]))

    def instr(self):
        w = self.w
        reg = self.reg
        ll = LocalLabels()
        # TODO check printable char and echo
        # TODO if not handle other
        return [self.char(), self.selector(), Rem("Not working yet")]


if __name__ == "__main__":
    log.critical("TESTING")
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
