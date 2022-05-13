""" 
    Allocte memory from the heap

    Bump allocator for now, read up on proper allocator.

    Buddy allocator is probably better for this.
"""

from boneless.arch.opcode import Instr
from boneless.arch.opcode import *

from ..firmware.base import *


class CopyMem(SubR):
    "Copy a block of memory"

    def setup(self):
        self.params = ["source", "destination", "count"]
        self.locals = ["counter", "holding"]

    def instr(self):
        w = self.w
        ll = LocalLabels()
        return [
            MOVI(w.counter, 0),
            ll("again"),
            LD(w.holding, w.source, 0),
            ST(w.holding, w.destination, 0),
            ADDI(w.source, w.source, 1),
            ADDI(w.destination, w.destination, 1),
            ADDI(w.counter, w.counter, 1),
            CMP(w.count, w.counter),
            BNE(ll.again),
        ]


class ModAlloc(SubR):
    "Move to MOD8 boundary and alloc some windows"

    def setup(self):
        self.params = ["size", "heap_pointer"]
        self.locals = ["offset", "current"]
        self.ret = ["pointer"]

    def instr(self):
        w = self.w
        ll = LocalLabels()
        return [
            Rem("Load the pointer"),
            LD(w.current, w.heap_pointer, 0),
            Rem("Align the pointer"),
            ANDI(w.offset, w.current, 16 - 1),  # last 3 bits
            CMPI(w.offset, 0),
            BEQ(ll.aligned),
            SUB(w.current, w.current, w.offset),
            ADDI(w.current, w.current, 8),
            ll("aligned"),
            Rem("Save the pointer"),
            MOV(w.pointer, w.current),
            Rem("Expand to windows * 8"),
            SLLI(w.size, w.size, 3),
            Rem("Move the pointer down size"),
            ADD(w.current, w.current, w.size),
            Rem("Save the heap_pointer"),
            ST(w.current, w.heap_pointer, 0),
        ]


class GAlloc(SubR):
    "Alloc from the global heap"

    def setup(self):
        self.params = ["size"]
        self.locals = ["heap"]
        self.ret = ["pointer"]

    def instr(self):
        w = self.w
        m = ModAlloc()
        return [
            Rem("Get the global heap pointer"),
            self.globals.heap_pointer(w.heap),
            m(w.size, w.heap, ret=[w.pointer]),
        ]


class Alloc(SubR):
    "Alloc some memory"

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
            self.globals.heap_pointer(w.heap_pointer),
            LD(w.current, w.heap_pointer, 0),
            Rem("Copy into the return position"),
            MOV(w.pointer, w.current),
            Rem("Move the pointer down size"),
            ADD(w.current, w.current, w.size),
            # ADDI(w.current, w.current, 1),
            ST(w.current, w.heap_pointer, 0),
        ]
