# Command enumeration for both sides of the link

from enum import IntEnum
from logging import NullHandler
from re import L

from boneless.arch.opcode import Instr
from boneless.arch.opcode import *

# the firmare constructs
from spork.firmware.base import *

from .packets import Transport
from .defines import FIRMWARE_VERSION, GATEWARE_VERSION, Commands
from .remote import GetVersion, GetDatablock
from .serial_link import MonInterface


class DataError(Exception):
    pass


class FirmVersionError(DataError):
    pass


class GateVersionError(DataError):
    pass


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
    def __init__(self, port="/dev/ttyUSB0", baud=115200):
        self._commands = {}
        self._mon = MonInterface(port=port, baud=baud)

    def _add(self, item):
        self._commands[item._id] = item
        # print(dir(item))
        setattr(self, item.__name__, item())

    def __repr__(self) -> str:
        self._mon.ping()
        return ""


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
    _mon = CL._mon

    def __init__(self):
        pass

    def local(self, *args):
        return self._mon.pack(self._id, 0, 0)

    def remote(self):
        command = Transport.NoComm
        command.mark()
        return command

    def __call__(self, *args):
        return self.local(*args)


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


@Attach()
class WriteData(Com):
    _id = Commands.write_data

    def local(self, *args):
        command = SendDatablock()
        command.mark()
        return command


@Attach()
class ReadData(Com):
    _id = Commands.read_data

    def remote(self):
        command = GetDatablock()
        command.mark()
        return command

    def local(self, address, size):
        comm = self._mon.pack(self._id, address, size)
        if size > 0:
            data = self._mon.data_read(size)
        else:
            return ()
        return data


@Attach()
class Version(Com):
    _id = Commands.version

    def remote(self):
        command = GetVersion()
        # command.mark()
        return command

    def local(self):
        val = self._mon.pack(self._id, 0, 0)
        data = self._mon.data_read(8)
        # Check version info
        firm_version = data[0]
        gate_version = data[1]
        if firm_version != FIRMWARE_VERSION:
            raise FirmVersionError()
        if gate_version != GATEWARE_VERSION:
            raise GateVersionError()

        return data


@Attach()
class Jump(Com):
    _id = Commands.jump


# @Attach()
class Free(Com):
    _id = Commands.free
