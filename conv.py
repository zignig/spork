" Number Processing Functions"


from boneless.arch.opcode import Instr
from boneless.arch.opcode import *

from ideal_spork.firmware.base import *
from ideal_spork.firmware.stringer import Stringer
from uartIO import UART
from switch import Switch

from ideal_spork.logger import logger

log = logger(__name__)

from rich import print

from collections import namedtuple

_fields = []  # [ 'start','stop','spill']


class Bork(type):
    def __new__(cls, instr):
        print(cls)
        print(instr._field_types)
        newinst = namedtuple()
        return super(Bork, cls)

    def list(self):
        print(dir(self))


def generate():
    l = Instr.mnemonics
    new_instr = {}
    for i, j in l.items():
        fields = list(j._field_types.keys())
        print(i, fields)
        new_instr[i] = namedtuple(i, fields)

    print(new_instr)
    return new_instr


val = generate()
