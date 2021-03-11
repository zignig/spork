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
            Rem("Copy into the return position"),
            MOV(w.heap_pointer, w.pointer),
            Rem("Move the pointer down size"),
            ADD(w.current, w.heap_pointer, w.size),
            ST(w.heap_pointer, w.current, 0),
        ]
