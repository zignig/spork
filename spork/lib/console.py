"Console"

from boneless.arch.opcode import Instr
from boneless.arch.opcode import *

from ..firmware.base import *
from .stringer import Stringer
from .uartIO import UART
from .ansi_codes import Term
from .warm import WarmBoot
from .switch import Switch
from .commands import MetaCommand
from .alloc import Alloc

from .action_list import Actions

from ..logger import logger

log = logger(__name__)

from rich import print


""" Console and string handling functions
    for a shell interface 
    [X] reset
    [X] warmboot
    [ ] echo
"""

# TODO add a working cursor


class CharPad(CodeObject):
    """
        A character pad with console editing
    """

    length = 32

    def setup(self):
        al = Alloc()
        return [Rem("setup the pad")]

    # TODO hard fail on overflow
    # Add functions for the Char pad here
    class Accept(SubR):
        def setup(self):
            self.params = ["pad_address", "char"]
            self.locals = ["length", "target_address", "pos"]

        def instr(self):
            w = self.w
            ll = LocalLabels()
            return [
                Rem("Copy the length"),
                LD(w.length, w.pad_address, 0),
                Rem("Load the cursor position"),
                LD(w.pos, w.pad_address, CharPad.length),
                Rem("Check against length"),
                CMPI(w.length, CharPad.length),
                BGTU(ll.exit),
                Rem("Add the length to the address"),
                # TODO do insert instead of append
                ADD(w.target_address, w.pad_address, w.length),
                ADDI(w.target_address, w.target_address, 1),
                ST(w.char, w.target_address, 0),
                Rem("Offset to the next char slot"),
                ADDI(w.length, w.length, 1),
                ST(w.length, w.pad_address, 0),
                Rem("Store the cursor"),
                ST(w.length, w.pad_address, CharPad.length),
                ll("exit"),
            ]

    def __init__(self, name="CharPad"):
        # attach to the firmware
        super().__init__()
        self.length = CharPad.length
        self.cursor = 0
        self.name = name
        self._used = False
        # Some internal functions
        self.accept = self.Accept()

    def __call__(self, register):
        self._used = True
        return [MOVR(register, self.name + self._postfix)]

    def cursor(self, register):
        return []

    def code(self):
        data = [Rem("Data Pad"), L(self.name + self._postfix), Rem("length")]
        data.extend([0] * self.length)
        data += [L("cursor" + self._postfix), Rem("cursor"), [0]]
        return data

    class BackSpace(SubR):
        "Backspace processor"

        def setup(self):
            self.params = ["charpad"]
            self.locals = ["length", "pos", "counter"]

        def instr(self):
            w = self.w
            reg = self.reg
            ll = LocalLabels()

            uart = UART()
            wh = uart.writeHex
            cr = uart.cr
            return [
                Rem("Load the length"),
                uart.cr(),
                LD(w.length, w.charpad, 0),
                LD(w.pos, w.charpad, CharPad.length),
                wh(w.length),
                uart.cr(),
                wh(w.pos),
            ]

    class Left(SubR):
        def setup(self):
            self.params = ["charpad"]
            self.locals = ["length", "pos", "counter", "temp"]

        def instr(self):
            w = self.w
            reg = self.reg
            ll = LocalLabels()

            uart = UART()
            term = Term()
            wh = uart.writeHex
            cr = uart.cr
            return [
                LD(w.pos, w.charpad, CharPad.length),
                CMPI(w.pos, 0),
                BEQ(ll.skip),
                SUBI(w.pos, w.pos, 1),
                ST(w.pos, w.charpad, CharPad.length),
                self.stringer.left(w.temp),
                term(w.temp),
                ll("skip"),
            ]

    class Right(SubR):
        def setup(self):
            self.params = ["charpad"]
            self.locals = ["length", "pos", "counter", "temp"]

        def instr(self):
            w = self.w
            reg = self.reg
            ll = LocalLabels()

            uart = UART()
            term = Term()
            wh = uart.writeHex
            cr = uart.cr
            return [
                LD(w.pos, w.charpad, CharPad.length),
                LD(w.length, w.charpad, 0),
                CMP(w.length, w.pos),
                BLEU(ll.skip),
                ADDI(w.pos, w.pos, 1),
                ST(w.pos, w.charpad, CharPad.length),
                self.stringer.right(w.temp),
                term(w.temp),
                ll("skip"),
            ]


class Console(SubR):
    # Subroutines inside the console

    def setup(self):
        self.params = ["char", "pad_address", "status"]
        self.locals = ["temp"]
        self.ret = ["status"]
        self.pad = CharPad()

    def build(self):
        # Bind the pad into the function
        log.critical("Build Console")

        # self.char = self.Char(self.w)

        self.selector = sel = Switch(self.w, self.w.char)
        ll = LocalLabels()
        self.uart = UART()
        self.wb = WarmBoot()
        self.bs = self.pad.BackSpace()
        self.left = self.pad.Left()
        self.right = self.pad.Right()

    def instr(self):
        w = self.w
        reg = self.reg
        ll = LocalLabels()
        List = MetaCommand.List()
        # Add some globals for the console
        self.globals.pad = 0
        self.globals.cursor = 0

        # make a CASE style selection
        sel = self.selector
        sel.add((9, [MOVI(w.status, Actions.COMPLETE)]))  # horizontal tab
        sel.add((8, [MOVI(w.status, Actions.BACKSPACE)]))  # b
        # CR does prompt for now
        sel.add((13, [MOVI(w.status, Actions.RUN)]))  # enter
        sel.add((27, [MOVI(w.status, Actions.ESCAPE)]))  # escape sequence
        # ^D Restart , warm boot
        sel.add(
            (
                4,
                [
                    Rem("^D reset"),
                    self.stringer.warmboot(self.w.temp),
                    self.uart.writestring(self.w.temp),
                    Rem("Wait for a while"),
                    MOVI(self.w.temp, 0xFFFF),
                    ll("again"),
                    SUBI(self.w.temp, self.w.temp, 1),
                    CMPI(self.w.temp, 0),
                    BZ(ll.out),
                    J(ll.again),
                    ll("out"),
                    MOVI(self.w.temp, 1),
                    Rem("Write to the warmboot device"),
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
                    # TODO make this a vector
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
    r = CharPad.SplitChomp()
    print(r.code())
    if False:
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
