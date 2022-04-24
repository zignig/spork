# Command enumeration for both sides of the link
from enum import IntEnum

MAGIC = 0x5A04


class Flags(IntEnum):
    First = 1 << 0
    Second = 1 << 1
    Other = 1 << 2

    @classmethod
    def scan(self, value):
        print(self, value)
        for i in self:
            print(i)


class Commands(IntEnum):
    hello = 1
    write_data = 2
    read_data = 3
    jump = 4
    write_external = 5
    read_external = 6
    load_code = 7
    read_code = 8
    delete_code = 9
    list_code = 10
    watch = 11
    reset = 12
    core_dump = 13
    unwind_stack = 14
    # and more


class CommandList:
    _index = 1

    def __init__(self):
        self._commands = {}

    def _add(self, item):
        self._commands[CommandList._index] = item
        CommandList._index += 1
        print(dir(item))
        setattr(self, item.__name__, item())


CL = CommandList()


def Attach(info=None):
    "Wrapper for registering commands"

    def inner(cls):
        print(info)
        print(cls, cls.__name__, dir(cls))
        CL._add(cls)
        return cls

    return inner


class Com:
    "Base serial command object"

    def __init__(self):
        print("bork")
        pass

    def local(self):
        print("LOCAL")

    def remote(self):
        print("REMOTE")

    def __call__(self):
        self.local()


# Base Imutable Commands
@Attach("hello")
class Hello(Com):
    def remote(self):
        pass


@Attach()
class Reset(Com):
    pass


@Attach("")
class WriteData(Com):
    pass


@Attach()
class ReadData(Com):
    pass
