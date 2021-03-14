"Allocte memory from the heap"

from boneless.arch.opcode import Instr
from boneless.arch.opcode import *

from ..firmware.base import *


class Alloc(SubR):
    " Alloc some memory "

    def setup(self):
        self.params = ["size"]
        self.locals = ["heap_pointer", "current"]
        self.ret = ["pointer"]

    def instr(self):
        # TODO track the heap pointer in a global
        # TODO warn on low memory hard fail on OOM
        w = self.w
        reg = self.reg
        ll = LocalLabels()
        # TODO check bounds and error out
        return [
            Rem("Load the current heap pointer"),
            self.globals.heap(w.heap_pointer),
            LD(w.current, w.heap_pointer, 0),
            Rem("Copy into the return position"),
            MOV(w.pointer, w.current),
            Rem("Move the pointer down size"),
            ADD(w.current, w.current, w.size),
            ADDI(w.current, w.current, 1),
            ST(w.current, w.heap_pointer, 0),
        ]
