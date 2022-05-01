# Command enumeration for both sides of the link
from enum import IntEnum
from logging import NullHandler
from re import L

# MAGIC = 0XBEEF

from boneless.arch.opcode import Instr
from boneless.arch.opcode import *

# the firmare constructs
from spork.firmware.base import *

from .packets import Transport
from .defines import Commands


class Flags(IntEnum):
    First = 1 << 0
    Second = 1 << 1
    Other = 1 << 2

    @classmethod
    def scan(self, value):
        print(self, value)
        for i in self:
            print(i)


class CommandList:
    def __init__(self):
        self._commands = {}

    def _add(self, item):
        self._commands[item._id] = item
        # print(dir(item))
        setattr(self, item.__name__, item())


CL = CommandList()


def Attach(info=None):
    "Wrapper for registering commands"

    def inner(cls):
        # print(info)
        # print(cls, cls.__name__, dir(cls))
        CL._add(cls)
        return cls

    return inner


class Dummy(SubR):
    def instr(self):
        # probably return error
        return []


class Com:
    "Base serial command object"
    _id = None

    def __init__(self):
        pass

    def local(self):
        print("LOCAL")

    def remote(self):
        command = Transport.NoComm
        command.mark()
        return command

    def __call__(self):
        self.local()


# Base Imutable Commands
@Attach("hello")
class Hello(Com):
    _id = Commands.hello

    class comm(SubR):
        def instr(self):
            return []

    def remote(self):
        command = Transport.Hello
        command.mark()
        return command


# @Attach()
class Version(Com):
    _id = Commands.version


# @Attach("")
class WriteData(Com):
    _id = Commands.write_data
    pass


# @Attach()
class ReadData(Com):
    _id = Commands.read_data
    pass


# @Attach()
class Jump(Com):
    _id = Commands.jump


# @Attach()
class Free(Com):
    _id = Commands.free
