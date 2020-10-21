"Serail to char and word reading and writing"

from boneless.arch.opcode import Instr
from boneless.arch.opcode import *

from ..firmware.base import *


class Alloc(SubR):
    " Alloc some memory "

    def setup(self):
        self.params = ["size"]
        self.locals = ["heap_pointer"]

    def instr(self):
        w = self.w
        reg = self.reg
        ll = LocalLabels()
        return []
