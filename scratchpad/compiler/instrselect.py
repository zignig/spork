# instruction selector

from boneless.arch.opcode import *
from .vartypes import *


class InstructionSelector:
    def __init__(self):
        self.table = {("add", Vint, "const"): ADDI}

    def select(self, find):
        print("find")
