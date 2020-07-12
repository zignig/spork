"Console"

from boneless.arch.opcode import Instr
from boneless.arch.opcode import *

from ideal_spork.firmware.base import *
from ideal_spork.firmware.stringer import Stringer
from uartIO import UART
from warm import WarmBoot
from switch import Switch
from commands import MetaCommand

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
            self.locals = ["length", "target_address"]

        def instr(self):
            w = self.w
            return [
                Rem("Copy the length"),
                LD(w.length, w.pad_address, 0),
                Rem("Add the length to the address"),
                # MOVI(w.target_address,1),
                ADD(w.target_address, w.pad_address, w.length),
                ADDI(w.target_address, w.target_address, 1),
                ST(w.char, w.target_address, 0),
                Rem("Offset to the next char slot"),
                ADDI(w.length, w.length, 1),
                ST(w.length, w.pad_address, 0),
            ]

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


class Console(SubR):
    # Subroutines inside the console

    def setup(self):
        self.params = ["char", "pad_address", "status"]
        self.locals = ["temp"]
        self.ret = ["status"]

    def build(self):
        # Bind the pad into the function
        self.pad = CharPad()

        # self.char = self.Char(self.w)

        self.selector = sel = Switch(self.w, self.w.char)
        ll = LocalLabels()
        self.uart = UART()
        self.wb = WarmBoot()

    def instr(self):
        w = self.w
        reg = self.reg
        ll = LocalLabels()
        List = MetaCommand.List()
        # make a CASE style selection
        sel = self.selector
        sel.add((9, [self.uart.cr(), List(), self.uart.cr()]))  # horizontal tab
        # CR does prompt for now
        sel.add((13, [MOVI(w.status, 20)]))
        # ^D Restart , warm boot
        sel.add(
            (
                4,
                [
                    Rem("^D reset"),
                    self.stringer.warmboot(self.w.temp),
                    self.uart.writestring(self.w.temp),
                    MOVI(self.w.temp, 0xFFFF),
                    ll("again"),
                    SUBI(self.w.temp, self.w.temp, 1),
                    CMPI(self.w.temp, 0),
                    BZ(ll.out),
                    J(ll.again),
                    ll("out"),
                    MOVI(self.w.temp, 1),
                    self.wb(self.w.temp),
                ],
            )
        )
        # ^C Init the firmware
        sel.add(
            (
                3,
                [
                    Rem("^C Init processor"),
                    self.stringer.reset(self.w.temp),
                    self.uart.writestring(self.w.temp),
                    J("init"),
                ],
            )
        )
        # TAB complete
        # ESCAPE

        # TODO if not handle other
        return [
            Rem("printable char"),
            CMPI(w.char, 31),
            BLEU(ll.cont),
            CMPI(w.char, 125),
            BGEU(ll.cont),
            Rem("Within Printable Range, echo char"),
            self.uart.write(w.char),
            self.pad.accept(w.pad_address, w.char),
            ll("cont"),
            Rem("Jump table select"),
            sel(),
            ll("exit"),
        ]


if __name__ == "__main__":
    log.critical("TESTING")
    console = Console()
    w = Window()
    w.req("val")
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
