"Actions to run on the console"

from boneless.arch.opcode import Instr
from boneless.arch.opcode import *
from spork.lib import console

from ..firmware.base import *

from .stringer import Stringer
from .switch import Switch
from .uartIO import UART
from .action_list import Actions, EscKeys
from .commands import MetaCommand
from .ansi_codes import Term

from ..logger import logger

log = logger(__name__)

from rich import print

term = Term()


class EscCode(SubR):
    "Write the escape code string"

    def setup(self):
        self.params = ["number"]
        self.locals = ["value", "address"]

    def instr(self):
        w = self.w
        ll = LocalLabels()
        u = UART()
        ws = u.writestring
        wh = u.writeHex
        return [
            # Zero start
            SUBI(w.number, w.number, 1),
            Rem("Grab the starting address of the table"),
            MOVR(w.address, "EscKeys"),
            Rem("Load the address"),
            ADD(w.address, w.address, w.number),
            Rem("Get the value"),
            LD(w.value, w.address, 0),
            Rem("offsets are relative, add to offset"),
            ADD(w.value, w.value, w.address),
            # u.cr(),
            # ws(w.value),
        ]


class dumpEsc(SubR):
    "Dump the enumerated string list"

    def setup(self):
        self.locals = ["value", "counter", "address", "limit"]

    def instr(self):
        w = self.w
        ll = LocalLabels()
        u = UART()
        ws = u.writestring
        wh = u.writeHex
        return [
            MOVI(w.limit, len(EscKeys)),
            MOVI(w.counter, 0),
            ll("again"),
            Rem("Grab the starting address of the table"),
            MOVR(w.address, "EscKeys"),
            ADD(w.address, w.address, w.counter),
            LD(w.value, w.address, 0),
            ADD(w.value, w.value, w.address),
            wh(w.counter),
            u.sp(),
            ws(w.value),
            u.cr(),
            ADDI(w.counter, w.counter, 1),
            CMP(w.counter, w.limit),
            BNE(ll.again),
            ll("end"),
        ]


class EscString(CodeObject):
    def __init__(self, enum):
        log.critical("build escape string")
        self._used = True
        super().__init__()
        self.enum = enum
        # Create a stringer
        self.st = Stringer()
        # Add all the enum tags to it
        for i in enum:
            self.st.add(str(i.value), i.name)
        # mark all the strings
        self.st.all()
        self._postfix = self.st._postfix

    def code(self):
        m = [L(self.enum.__qualname__), Rem(self.enum.__qualname__), Rem(self._postfix)]
        for i in self.enum:
            lref = str(i.value) + self._postfix
            # m.append(Rem(lref))
            m.append(Ref(lref))
        return m


class EscapeAction(SubR):
    def setup(self):
        self.params = ["command", "charpad"]

    def build(self):
        self.selector = Switch(self.w, self.w.command)

    def instr(self):
        u = UART()
        ws = u.writestring
        wh = u.writeHex
        w = self.w
        reg = self.reg
        ll = LocalLabels()
        cons = console.Console()
        esccode = EscCode()
        sel = self.selector
        sel.add((EscKeys.DEL, cons.bs(w.charpad)))
        sel.add((EscKeys.LEFT, cons.left(w.charpad)))
        sel.add((EscKeys.RIGHT, cons.right(w.charpad)))
        return [
            Rem("Escape Key Actions"),
            esccode(w.command),
            sel(),
        ]  # ,u.cr(),wh(w.charpad)]


class Escaper(SubR):
    "Process the escape sequence"
    e = EscString(EscKeys)

    def setup(self):
        self.locals = ["temp", "command", "char", "counter"]
        self.ret = ["status"]

    def build(self):
        # Build the selectors
        self.selector = Switch(self.w, self.w.char)
        self.sel2 = Switch(self.w, self.w.char)
        self.sel3 = Switch(self.w, self.w.char)

    def instr(self):
        w = self.w
        reg = self.reg
        ll = LocalLabels()
        uart = UART()

        # selectors for the char
        sel = self.selector
        sel2 = self.sel2
        sel3 = self.sel3

        self.stringer.has_next = "2 char , start 1"
        self.stringer.nomore = "no more"
        # Single char selector
        sel.add(("A", MOVI(w.status, EscKeys.UP)))
        sel.add(("B", MOVI(w.status, EscKeys.DOWN)))
        sel.add(("C", MOVI(w.status, EscKeys.RIGHT)))
        sel.add(("D", MOVI(w.status, EscKeys.LEFT)))
        sel.add(("3", MOVI(w.status, EscKeys.DEL)))
        sel.add(("4", MOVI(w.status, EscKeys.END)))
        sel.add(("5", MOVI(w.status, EscKeys.PGUP)))
        sel.add(("6", MOVI(w.status, EscKeys.PGDOWN)))
        # second char @ 1
        sel2.add(("~", MOVI(w.status, EscKeys.HOME)))
        sel2.add(("1", MOVI(w.status, EscKeys.F1)))
        sel2.add(("2", MOVI(w.status, EscKeys.F2)))
        sel2.add(("3", MOVI(w.status, EscKeys.F3)))
        sel2.add(("4", MOVI(w.status, EscKeys.F4)))
        sel2.add(("5", MOVI(w.status, EscKeys.F5)))
        # Weird Jump in keys ?
        sel2.add(("7", MOVI(w.status, EscKeys.F6)))
        sel2.add(("8", MOVI(w.status, EscKeys.F7)))
        sel2.add(("9", MOVI(w.status, EscKeys.F8)))
        # second char @ 2
        sel3.add(("~", MOVI(w.status, EscKeys.INS)))
        sel3.add(("0", MOVI(w.status, EscKeys.F9)))
        sel3.add(("1", MOVI(w.status, EscKeys.F10)))
        sel3.add(("3", MOVI(w.status, EscKeys.F11)))
        sel3.add(("4", MOVI(w.status, EscKeys.F12)))
        return [
            Rem("Check if there are any more chars"),
            Rem("have to wait for the next char to arrive"),
            MOVI(w.counter, 0x1FF),
            ll("wait"),
            SUBI(w.counter, w.counter, 1),
            CMPI(w.counter, 0),
            BNE(ll.wait),
            Rem("Now we can check for the char"),
            uart.read(ret=[w.char, w.status]),
            CMPI(w.status, 0),
            BEQ(ll.nomore),
            Rem("Consumes the ["),
            uart.read(ret=[w.char, w.status]),
            # uart.write(w.char),
            CMPI(w.status, 0),
            BEQ(ll.nomore),
            Rem("directions"),
            Rem("check for double char entries"),
            [CMPI(w.char, ord("1")), BEQ(ll.double1)],
            [CMPI(w.char, ord("2")), BEQ(ll.double2)],
            Rem("Single char escape code"),
            Rem("select char and map to Enum"),
            sel(),
            J(ll.cont),
            ll("double1"),
            Rem("Check for a third char"),
            uart.read(ret=[w.char, w.status]),
            CMPI(w.status, 0),
            BEQ(ll.cont),
            sel2(),
            J(ll.cont),
            ll("double2"),
            uart.read(ret=[w.char, w.status]),
            CMPI(w.status, 0),
            BEQ(ll.cont),
            sel3(),
            J(ll.cont),
            ll("nomore"),
            MOVI(w.status, EscKeys.ESC),
            ll("cont"),
            ll("end"),
        ]


class Action(SubR):
    "Action switch from the console status"

    def setup(self):
        self.params = ["pad_address", "status"]
        self.locals = ["temp", "command"]
        self.ret = ["status"]

    def build(self):
        # Bind the pad into the function
        self.selector = Switch(self.w, self.w.status)
        self.esc = Escaper()

    def instr(self):
        w = self.w
        reg = self.reg
        ll = LocalLabels()
        uart = UART()
        List = MetaCommand.List()
        Search = MetaCommand.Search()
        Run = MetaCommand.Run()
        EscA = EscapeAction()
        esccode = EscCode()
        cons = console.Console()
        # make a CASE style selection
        sel = self.selector
        self.stringer.notfound = "Command not found :"
        sel.add(
            (
                Actions.RUN,  # find a command if any and run.
                [
                    Rem("Search for a matching command and run"),
                    Rem("Check for empty command"),
                    LD(w.temp, w.pad_address, 0),
                    CMPI(w.temp, 0),
                    BZ(ll.cont),
                    uart.cr(),
                    Search(w.pad_address, ret=[w.status, w.command]),
                    CMPI(w.status, 1),
                    BNE(ll.skip),
                    # uart.writeHex(w.command),
                    Rem("Reset the pad"),
                    MOVI(w.status, 0),
                    ST(w.status, w.pad_address, 0),
                    Rem("Found a command run"),
                    Run(w.command),
                    J(ll.cont),
                    ll("skip"),
                    self.stringer.notfound(w.temp),
                    uart.writestring(w.temp),
                    ll("cont"),
                    uart.writestring(w.pad_address),
                    Rem("Reset the pad"),
                    MOVI(w.status, 0),
                    ST(w.status, w.pad_address, 0),
                    ST(w.status, w.pad_address, console.CharPad.length),
                    uart.cr(),
                    self.stringer.prompt(self.w.temp),
                    uart.writestring(self.w.temp),
                ],
            )
        )
        sel.add(
            (
                Actions.ESCAPE,  # escape sequence
                [self.esc(ret=[w.status]), EscA(w.status, self.w.pad_address)],
            )
        )
        sel.add(
            # make this an escape sequence, to process the same as the outers.
            (
                Actions.BACKSPACE,  # escape sequence
                [MOVI(w.status, EscKeys.BS), EscA(w.status, self.w.pad_address)],
            )
        )
        sel.add(
            (
                Actions.COMPLETE,  # tab complete
                [
                    Rem("list all commands"),
                    List(),
                    self.stringer.prompt(self.w.temp),
                    uart.writestring(self.w.temp),
                    uart.writestring(w.pad_address),
                ],
            )
        )
        return [sel()]


if __name__ == "__main__":
    log.critical("Action Testing")
