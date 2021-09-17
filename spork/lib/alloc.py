"Allocte memory from the heap"

from boneless.arch.opcode import Instr
from boneless.arch.opcode import *

from ..firmware.base import *


class ModAlloc(SubR):
    " Move to MOD8 boundary and alloc some windows"

    def setup(self):
        self.params = ["size", "heap_pointer"]
        self.locals = ["offset", "current"]
        self.ret = ["pointer", "heap_pointer"]

    def instr(self):
        w = self.w
        reg = self.reg
        ll = LocalLabels()
        return [
            Rem("Align the pointer"),
            ANDI(w.heap_pointer, w.offset, 16 - 1),  # last 3 bits
            CMPI(w.offset, 0),
            BEQ(ll.aligned),
            SUB(w.heap_pointer, w.offset, w.heap_pointer),
            ADDI(w.heap_pointer, w.heap_pointer, 8),
            ll("aligned"),
            LD(w.current, w.heap_pointer, 0),
            Rem("Copy into the return position"),
            MOV(w.pointer, w.current),
            Rem("Expand to windows * 8"),
            SRLI(w.size, w.size, 3),
            Rem("Move the pointer down size"),
            ADD(w.current, w.current, w.size),
            MOV(w.current, w.heap_pointer),
        ]


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
            # ADDI(w.current, w.current, 1),
            ST(w.current, w.heap_pointer, 0),
        ]
