" Set of base commands "

from boneless.arch.opcode import Instr
from boneless.arch.opcode import *

from .commands import Command
from ..firmware.base import *

from .uartIO import UART

uart = UART()


class Dump(Command):
    class _dump(SubR):
        def setup(self):
            self.locals = ["tmp"]
            self.mark()

        def instr(self):
            return [uart.cr(), uart.core(), uart.cr()]

    call = _dump()


class Reset(Command):
    class _reset(SubR):
        def setup(self):
            self.mark()

        def instr(self):
            return [J("init")]

    call = _reset()


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


class _helptext(SubR):
    def setup(self):
        self.locals = ["tmp"]
        self.mark()

    def instr(self):
        self.stringer.helper = """
Please refer to 

    https://github.com/zignig/spork

For more information
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
