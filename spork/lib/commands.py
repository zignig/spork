" Command infrastructure"

from boneless.arch.opcode import Instr
from boneless.arch.opcode import *


from .uartIO import UART

from ..firmware.base import *
from .stringer import SingleString

from rich import print

from ..logger import logger

log = logger(__name__)

# TODO , convert to radix tree ?

# debugging
def r(val):
    print(val)


class MetaCommand(type):
    commands = []
    """
    Meta Command is a class for collecting all the commands together
    """

    def __new__(cls, clsname, bases, attrs):
        newclass = super(MetaCommand, cls).__new__(cls, clsname, bases, attrs)
        cls.register(newclass)  # here is your register function
        return newclass

    def register(cls):
        d = MetaCommand.commands
        if cls.__qualname__ == "Command":
            # Don't add root subclass
            return
        if cls not in d:
            log.debug("ADD COMMAND %s", cls.__qualname__)
            d.append(cls())

    @classmethod
    def code(cls):
        li = MetaCommand.commands
        # loop through and add commands to the list
        # assemble the commands
        c = []
        for i in li:
            c.append(i)
        li[0].next = "first_command"
        # attach a pointer to the next command
        for i, j in enumerate(li[1:]):
            li[i].next = j.label

        li[-1].next = "last_command"

        out = [L("first_command")]
        for i in li:
            out.append(i.code())
        out.append(L("last_command"))

        return out

    class Search(SubR):
        "search for a given command and return a pointer"
        __unfinished = True

        def setup(self):
            self.params = ["command", "status"]
            self.ret = ["status"]
            self.locals = ["start", "end", "count"]

        def instr(self):
            w = self.w
            ll = LocalLabels()
            return [
                Rem("load the pointer of the first command"),
                MOVR(w.start, "first_command"),
                Rem("Load the end of the commands"),
                MOVR(w.end, "last_command"),
                Rem("Load the string of the current command"),
                ll("again"),
                Rem("Move to the start of the string"),
                ADDI(w.current, w.start, 1),
                Rem("Write the string"),
                uart.writestring(w.current),
                uart.cr(),
                Rem("Jump to the next command"),
                LD(w.incr, w.start, 0),
                ADD(w.start, w.start, w.incr),
                Rem("Are we at the end"),
                CMP(w.start, w.end),
                BNE(ll.again),
            ]

    class List(SubR):
        " List all the available commands"

        def setup(self):
            self.locals = ["incr", "start", "end", "current"]

        def instr(self):
            w = self.w
            ll = LocalLabels()
            uart = UART()
            return [
                uart.cr(),
                Rem("load the pointer of the first command"),
                MOVR(w.start, "first_command"),
                Rem("Load the end of the commands"),
                MOVR(w.end, "last_command"),
                Rem("Load the string of the current command"),
                ll("again"),
                Rem("Move to the start of the string"),
                ADDI(w.current, w.start, 1),
                Rem("Write the string"),
                uart.writestring(w.current),
                uart.cr(),
                Rem("Jump to the next command"),
                LD(w.incr, w.start, 0),
                ADD(w.start, w.start, w.incr),
                Rem("Are we at the end"),
                CMP(w.start, w.end),
                BNE(ll.again),
            ]


class Command(metaclass=MetaCommand):
    def __init__(self):
        self.next = None
        self.post_fix = "_comm"
        if not hasattr(self, "name"):
            self.name = type(self).__qualname__
        self.commname = SingleString(self.name, self.name.lower(), "", compact=False)

    def __repr__(self):
        t = self.label + " --> "
        t += str(self.next) + "\n"
        # t += str(self.code())
        return t

    @property
    def label(self):
        return self.name + self.post_fix

    def ref(self, val):
        " ref resolver for assembler"

        def relocate(resolver):
            return resolver(val)

        return relocate

    def instr(self):
        return []

    def code(self):
        return [
            L(self.label),
            self.ref(self.next),
            self.commname.as_mem(),
            self.instr(),
        ]


class LedON(Command):
    pass


class LedOFF(Command):
    pass


class Timer(Command):
    pass


class Warm(Command):
    pass


class Load(Command):
    pass


class Save(Command):
    pass


class List(Command):
    pass


class Demo(Command):
    pass


class Help(Command):
    pass


class ShortHelp(Command):
    name = "?"


class Start(Command):
    pass


class Stop(Command):
    pass


class Export(Command):
    pass


if __name__ == "__main__":
    c = MetaCommand.code()
    print(c)
    fw = Instr.assemble(c)
    print(fw)

# working jump refs


def test():
    def jump_table(*args):
        def relocate(resolver):
            return [resolver(arg) for arg in args]

        return relocate

    def ref(val):
        def relocate(resolver):
            return resolver(val)

        return relocate

    return [
        J("end"),
        jump_table("foo", "bar", "baz"),
        J("end2"),
        L("end"),
        0,
        L("foo"),
        0,
        L("bar"),
        0,
        L("baz"),
        0,
        L("end2"),
        ref("hello"),
        ref("hello"),
        0,
        0,
        0,
        L("hello"),
        15,
        0,
        0,
        ref("hello"),
    ]


# a = test()
# print(a)
# fw = Instr.assemble(a)
# print(fw)
