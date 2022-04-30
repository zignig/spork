#!/usr/bin/python


# make a firmware object
# enumerate the commands from commands
# with some spares and handle comms

from re import I
from boneless.arch.opcode import Instr
from boneless.arch.opcode import *

# the firmare constructs
from spork.firmware.base import *
from spork.firmware.firmware import Firmware

# from .commands import Commands , CL
from spork.lib.switch import Switch

# the library code
from spork.lib.uartIO import UART

from spork.logger import logger

log = logger(__name__)

from spork.lib.monitor.packets import Transport
from spork.lib.monitor.commands import CL

trans = Transport()


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
        for i in CL._commands:
            command = CL._commands[i]().remote()
            if command is not None:
                val = Ref(command.name)
            else:
                val = Ref(self.dummy.name)

            li.append([Rem(i), val])
        # li.append(ll('jvt_end'))
        return li

    def vector_len(self):
        return len(CL._commands)

    def instr(self):
        w = self.w
        ll = LocalLabels()

        s = Switch(w, w.command)
        for i in CL._commands:
            command = CL._commands[i]().remote()
            s.add((i, [Rem(i), command()]))

        return [
            Rem("Command Switcher"),
            trans.Recv(ret=[w.command, w.param1, w.param2, w.status]),
            CMPI(w.command, self.vector_len()),
            BGTU(ll.command_overflow),
            s(),
            # Rem("Save the jump return"),
            # MOVR(w.ret,ll.end_vt),
            # Rem("Jump through the switch table"),
            # J(ll.end_vt),
            # JVT(w.command,0),
            # ll('vt'),
            # self.vector(),
            ll("end_vt"),
            J(ll.end),
            ll("command_overflow"),
            Transport.Error(),
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
        ]


" load this "
firmware = MonitorFirm

if __name__ == "__main__":
    from spork.upload import Uploader
    import fwtest

    spork = fwtest.build(MonitorFirm, detail=True)
    up = Uploader()
    up.upload(spork, console=False)
