#!/usr/bin/python


# make a firmware object
# enumerate the commands from commands
# with some spares and handle comms

from re import I
from boneless.arch.opcode import Instr
from boneless.arch.opcode import *

# the firmare constructs
from ...firmware.base import *
from ...firmware.firmware import Firmware

# from .commands import Commands , CL
from ..switch import Switch

# the library code
from spork.lib.uartIO import UART

from spork.logger import logger

log = logger(__name__)

from .packets import Transport
from .commands import CommandList
from .defines import Commands
from .remote import DataBlock, VersionInformation

# Create the subroutines
datablock = DataBlock()
trans = Transport()

CL = CommandList()


class OtherStuff(SubR):
    def instr(self):
        return []


class MonAction(SubR):
    "Monitor action switcher"
    locals = ["command", "param1", "param2", "status", "rcomm"]

    def vector(self):
        # create a vector table for commands
        ll = LocalLabels()
        li = []
        # li = [Ref(self.dummy.name)]
        # li = [J(ll.jvt_end)]
        # rr = Ref(CL._commands[Commands.hello]().remote().name)
        # li = [rr,rr,rr,rr,rr,rr,rr,rr]
        # return li
        for i in CL._commands:
            command = CL._commands[i]().remote()
            if command is not None:
                val = Ref(command.name)
            li.append([Rem(i), val])
        # li.append(ll('jvt_end'))
        return li

    def vector_len(self):
        "Length of available Commands"
        return len(CL._commands)

    def instr(self):
        w = self.w
        ll = LocalLabels()
        SwitchCommand = Switch(w, w.command)
        for i in CL._commands:
            command = CL._commands[i]().remote()

            SwitchCommand.add(
                (i, [Rem(i), command(w.param1, w.param2, ret=[w.status])])
            )

        return [
            Rem("Command Switcher"),
            trans.Recv(ret=[w.command, w.param1, w.param2, w.status]),
            CMPI(w.status, 0),
            BNE(ll.end),  # Propagate status up
            CMPI(w.command, self.vector_len()),
            BGTU(ll.command_overflow),
            Rem("Use a switch table"),
            SwitchCommand(),
            Rem("Can't get switch tables working"),
            # Rem("Save the jump return"),
            # MOVR(w.ret, ll.end_vt),
            # J('SendHelloResp'),
            # trans.Send(w.command, w.ret, w.status),
            # MOVI(w.command,1),
            # Rem("Jump through the switch table"),
            # JST(w.command,-1),
            # self.vector(),
            # ll("end_vt"),
            J(ll.end),
            ll("command_overflow"),
            Transport.Error(w.param1, w.param2),
            # trans.Send(w.command, w.param1, w.param2),
            ll("end"),
        ]


# Working Functions``
os = OtherStuff()
ma = MonAction()


class MonitorFirm(Firmware):
    def setup(self):
        self.w.req(["value"])

    def instr(self):
        w = self.w
        reg = self.reg
        ll = LocalLabels()
        return [
            Rem("Loop and Wait for serial"),
            LDXA(w.value, reg.serial.rx.rdy),
            CMPI(w.value, 0),
            BEQ(ll.over),
            ma(),
            ll("over"),
            os(),
            # DataBlock.Read(w.value,w.value,ret=[w.value]),
            # DataBlock.Write(w.value,w.value),
        ]


" load this "
firmware = MonitorFirm

if __name__ == "__main__":
    from spork.upload import Uploader
    import fwtest

    spork = fwtest.build(MonitorFirm, detail=True)
    up = Uploader()
    up.upload(spork, console=False)  # , console=True)
    # r = Instr.disassemble(spork.fw.assemble())
    # for i in enumerate(r):
    #   print(i)
