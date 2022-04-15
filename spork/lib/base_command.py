" Set of base commands "

from boneless.arch.opcode import Instr
from boneless.arch.opcode import *

from .commands import Command
from .ansi_codes import Term
from ..firmware.base import *

from .uartIO import UART

uart = UART()
term = Term()


class Dump(Command):
    class _dump(SubR):
        def setup(self):
            self.locals = ["tmp"]
            self.mark()

        def instr(self):
            return [uart.cr(), uart.core(), uart.cr()]

    call = _dump()


class ClearLine(Command):
    name = "cl"

    class _cl(SubR):
        def setup(self):
            self.locals = ["temp"]
            self.mark()

        def instr(self):
            w = self.w
            return [self.stringer.br(w.temp), term(w.temp)]

    call = _cl()


class ClearScreen(Command):
    name = "clear"

    class _cls(SubR):
        def setup(self):
            self.locals = ["temp"]
            self.mark()

        def instr(self):
            w = self.w
            return [
                self.stringer.clearscreen(w.temp),
                term(w.temp),
                self.stringer.home(w.temp),
                term(w.temp),
            ]

    call = _cls()


class JumpToBootloader(Command):
    name = "BL3_"
    case = True

    class _bl(SubR):
        def setup(self):
            self.mark()

        def instr(self):
            return [MOVI(R0, 0), JR(R0, 0)]

    call = _bl()


class Reset(Command):
    class _reset(SubR):
        def setup(self):
            self.mark()

        def instr(self):
            return [J("init")]

    call = _reset()


class Demo(Command):
    class _demo(SubR):
        " turn this into a fancy demo"

        def setup(self):
            self.locals = ["tmp"]
            self.mark()

        def instr(self):
            self.stringer.demo = (
                "This is actually a really fancy ANSI demo, no really..."
            )
            w = self.w
            return [
                uart.cr(),
                self.stringer.demo(w.tmp),
                uart.writestring(w.tmp),
                uart.cr(),
            ]

    call = _demo()


class Out(Command):
    class outtest(SubR):
        def setup(self):
            self.locals = ["tmp"]
            self.mark()

        def instr(self):
            self.stringer.hello = "this is a test"
            w = self.w
            return [
                uart.cr(),
                self.stringer.hello(w.tmp),
                uart.writestring(w.tmp),
                uart.cr(),
            ]

    call = outtest()


class Warm(Command):
    class _warmer(SubR):
        def setup(self):
            self.locals = ["temp"]
            self.mark()

        def instr(self):
            reg = self.reg
            w = self.w
            return [
                MOVI(w.temp, 1),
                STXA(w.temp, reg.warm.image),
                STXA(w.temp, reg.warm.en),
            ]

    call = _warmer()


class Prog(Command):
    class _prog(SubR):
        def setup(self):
            self.locals = ["temp"]
            self.mark()

        def instr(self):
            reg = self.reg
            w = self.w
            return [
                MOVI(w.temp, 0),
                STXA(w.temp, reg.warm.image),
                MOVI(w.temp, 1),
                STXA(w.temp, reg.warm.en),
            ]

    call = _prog()


class _helptext(SubR):
    def setup(self):
        self.locals = ["tmp"]
        self.mark()

    def instr(self):
        self.stringer.helper = """
<tab> List commands
^C reset
^D warmboot into the bootloader
^] exit shell

refer to https://github.com/zignig/spork/
        """
        w = self.w
        return [
            uart.cr(),
            self.stringer.helper(w.tmp),
            uart.writestring(w.tmp),
            uart.cr(),
        ]


class Help(Command):
    call = _helptext()


class ShortHelp(Command):
    name = "?"
    call = _helptext()
