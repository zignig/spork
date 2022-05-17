"""
    Command enumeration for both sides of the link

"""


from enum import IntEnum

# stuff for the link
from .packets import Transport
from .defines import FIRMWARE_VERSION, GATEWARE_VERSION, Commands, MemoryBlock
from .remote import GetVersion, GetDataBlock, Jumper, SendDataBlock, AllocBlock
from .serial_link import MonInterface

# Some errors
class DataError(Exception):
    pass


class FirmVersionError(DataError):
    pass


class GateVersionError(DataError):
    pass


class CommandList:
    "Interactive monitor for the Boneless"
    _commands = {}

    def __init__(self, port="/dev/ttyUSB0", baud=115200):
        self._mon = MonInterface(port=port, baud=baud)
        Com._mon = self._mon

    @classmethod
    def _add(self, item):
        CommandList._commands[item._id] = item
        # print(dir(item))
        setattr(self, item.__name__, item())

    def __repr__(self) -> str:
        val = ""
        self._mon.ping()
        val += self.__doc__ + "\n\n Available Commands \n\n"
        for _, i in self._commands.items():
            val += i.__name__ + "\n"
            if hasattr(i, "__doc__") and i.__doc__ is not None:
                val += "\t" + i.__doc__ + "\n"
        return val


# CL = CommandList()


def Attach(info=None):
    "Wrapper for registering commands"

    def inner(cls):
        # print(info)
        # print(cls, cls.__name__, dir(cls))
        CommandList._add(cls)
        return cls

    return inner


class Com:
    "Base serial command object"
    _id = None
    _mon = None

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
    "send a ping and get a pong"
    _id = Commands.hello

    def remote(self):
        command = Transport.Hello
        command.mark()
        return command


@Attach()
class WriteData(Com):
    "write data to memory ( address , (data) )"
    _id = Commands.write_data

    def remote(self, *args):
        command = SendDataBlock()
        command.mark()
        return command

    def local(self, address, data):
        size = len(data)
        comm = self._mon.pack(self._id, address, size)
        if size > 0:
            self._mon.data_write(data)


@Attach()
class ReadData(Com):
    "read data from memory (address,size)"
    _id = Commands.read_data

    def remote(self):
        command = GetDataBlock()
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
    "get version data of firmware and hardware"
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
    "Execute code at (address)"
    _id = Commands.jump

    def remote(self):
        command = Jumper()
        return command

    # local is single packet
    # default does that


@Attach()
class Alloc(Com):
    "Allocate (size) * 8 words"
    _id = Commands.alloc

    def remote(self):
        command = AllocBlock()
        return command

    def local(self, size):
        alloc = self._mon.pack(self._id, size, 0)
        block = MemoryBlock(alloc[1], alloc[2])
        return block


@Attach()
class Free(Com):
    "show remaining memory"
    pass


# @Attach()
# class LoadCode(Com):
#     _id = Commands.load_code
