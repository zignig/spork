" Weird meta lcass thing"


from boneless.arch.opcode import Instr
from boneless.arch import asm
from boneless.arch.opcode import *


from rich import print

from collections import namedtuple


class SpillError(Exception):
    pass


class Register:
    def __init__(self, name, parent):
        self.name = name
        self.parent = parent
        # self.active = False
        self.loaded = False
        self.spilt = False
        self.offset = None
        self.current = None

    def __repr__(self):
        return (
            self.name
            + ":"
            + str(self.current)
            + ":"
            + str(self.loaded)
            + ":"
            + str(self.offset)
        )

    def release(self, current):
        return self.parent.release(self, current)

    def resolve(self):
        if not self.loaded:
            self.current = self.parent.req()
            self.loaded = True
        return self.current


class Window:
    " Automatic Window class"
    max = 6

    def __init__(self):
        self.registers = []
        self.spill = False
        self.free = [R0, R1, R2, R3, R4, R5]
        self.used = []
        self.offset = 9

    def req(self):
        if len(self.free) > 0:
            f = self.free.pop(0)
            self.used.append(f)
            print("ALLOCATE", f)
            return f
        else:
            print("RUNOUT")
            raise SpillError()

    def release(self, target, current):
        # release a register
        instr = []
        print("target ", target)
        for i in self.registers:
            if i.current not in current:
                if i.loaded == True:
                    i.loaded = False
                    print("choose", i)
                    if i.offset == None:
                        i.offset = self.offset
                        self.offset += 1
                    if target.offset == None:
                        target.offset = self.offset
                        self.offset += 1
                    print("target ", target)
                    print("copy out ", i.current)
                    instr.append(ST(i.current, R6, i.offset))
                    i.spilt = True
                    print("load in")
                    if not target.spilt:
                        instr.append(LD(i.current, R6, target.offset))
                    print("return instruction")
                    target.loaded = True
                    target.current = i.current
                    current.append(i.current)
                    i.current = None
                    break
        return instr

    def __getattr__(self, name):
        if name not in self.registers:
            new_reg = Register(name, self)
            setattr(self, name, new_reg)
            self.registers.append(new_reg)

        return getattr(self, name)


class over:
    def cool(self):
        print("Cool")

    def encode(self):
        return []

    def __call__(self, num):
        " Weird meta thing"
        att = {}
        spill = False
        spilled = {}
        current = []
        for i in self._fields:
            # Check all the registers
            val = getattr(self, i)
            print(val)
            if isinstance(val, Register):
                try:
                    val = val.resolve()
                    current.append(val)
                except:
                    spill = True
                    spilled[i] = val

            att[i] = val
        # If the the registers are loaded , just return the instruction
        # directly
        if not spill:
            return self._instr(**att)
        print(att)
        print(current)
        print(spilled)
        spill_code = []
        for i in spilled:
            reg = spilled[i]
            spill_code.append(reg.release(current))
            att[i] = reg.resolve()
            print("no active for", i)
        spill_code.append(self._instr(**att))
        return spill_code


def generate():
    l = Instr.mnemonics
    other = {}
    for i, j in l.items():
        fields = list(j._field_types.keys())
        field_dict = {}
        for k in fields:
            field_dict[k] = None
        twister = namedtuple(i, field_dict)
        other[i] = type(i, (twister, over), {"_instr": j, "_fields": fields})

    return other


other = generate()
o = other["OR"]
w = Window()
v = Instr.assemble(o(w.a, w.b, w.c))
o(w.d, w.e, w.f)(0)
print(v)
