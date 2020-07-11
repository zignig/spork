" Command infrastructure"

from boneless.arch.opcode import Instr
from boneless.arch.opcode import *


from ideal_spork.firmware.base import *
from ideal_spork.firmware.stringer import SingleString

from rich import print


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
            d.append(cls())

    @classmethod
    def code(cls):
        li = MetaCommand.commands
        # loop through and add sub-subroutines to the list
        c = [L("main")]
        old = "main"
        for i in li:
            i.back = old
            c.append(i.code())
            old = i.label
        return c


class Command(metaclass=MetaCommand):
    def __init__(self):
        self.back = None
        self.forward = None
        self.post_fix = "_comm"
        if not hasattr(self, "name"):
            self.name = type(self).__qualname__
            self.commname = SingleString(self.name, self.name.lower(), self.post_fix)

    @property
    def label(self):
        return self.name + self.post_fix

    def ref(self, val):
        " ref resolver for assembler"

        def relocate(resolver):
            return resolver(val)

        return relocate

    def instr(self):
        return [0, 1, 1]

    def code(self):
        return [self.ref(self.back), self.commname.as_mem(), self.instr()]


class Hello(Command):
    pass


class FNORD(Command):
    pass


class List(Command):
    pass


class Help(Command):
    def instr(self):
        return [1, 2, 3, 4, 5, 6, 7, 8, 9, 0]


class GO(Command):
    pass


print(MetaCommand.commands)

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
