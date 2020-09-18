" Wrapping all instructions for register allocation"

# nod to https://github.com/tpwrules/ice_panel/blob/regalloc/regalloc.py
# try this https://en.wikipedia.org/wiki/Register_allocation#Linear_Scan
# https://web.cs.wpi.edu/~cs544/PLT11.6.3.html
# http://www.brainkart.com/subject/Compiler-Design_133/

import boneless
from boneless.arch.opcode import Instr
from boneless.arch import asm
from boneless.arch import opcode
from boneless.arch.opcode import R0, R1, R2, R3, R4, R5, R6, R7, L

from ..firmware.base import *

from rich import print

from collections import namedtuple

__working__ = False


class Wrapper:
    """ Wrapping instructions for register allocation"""

    def allocate(self):
        " Low quality request allocator "
        att = {}
        spill = False
        spilled = {}
        current = []
        for i in self._fields:
            # Check all the registers
            val = getattr(self, i)
            # print(val)
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
        # print(att)
        # print(current)
        # print(spilled)
        spill_code = []
        for i in spilled:
            reg = spilled[i]
            spill_code.append(reg.release(current))
            att[i] = reg.current
        spill_code.append(self._instr(**att))
        # print(spill_code)
        return spill_code


def WrapBonelessInstructions():
    # Build wrapped instructions for new window
    l = Instr.mnemonics
    other = {}
    for i, j in l.items():
        fields = list(j._field_types.keys())
        field_dict = {}
        for k in fields:
            field_dict[k] = None
        twister = namedtuple(i, field_dict)
        other[i] = type(i, (twister, Wrapper), {"_instr": j, "_fields": fields})
    # attach to the module ( cursed )
    for i, j in other.items():
        globals()[i] = j
    return other


class BasicBlock:
    def __init__(self):
        self.code = []
        self.registers = set()

    def GetReg(self):
        " get all the registers in this basic block"
        for i, j in self.code:
            if hasattr(j, "_fields"):
                for k in j._fields:
                    val = getattr(j, k)
                    if isinstance(val, Register):
                        self.registers.add(val)

    def add(self, value):
        self.code.append(value)


# Create a set op wrapped
other = WrapBonelessInstructions()


def ListOfInstructions():
    l = boneless.arch.opcode.__all__
    l = list(Instr.mnemonics.keys())
    return l


__all__ = ListOfInstructions()


class SpillError(Exception):
    pass


class Register:
    """ Register wrapper for allocation """

    debug = False

    def __init__(self, name, parent, locked=False):
        self.name = name
        self.parent = parent

        self.live = False
        self.dirty = False
        self.loaded = False
        self.spilt = False
        self.offset = None
        self.current = None
        self.locked = locked
        # usage count
        self.count = 0
        # active intervals
        self.start = None
        self.finish = None

    def within(self, val):
        if (val >= self.start) and (val <= self.finish):
            return True
        return False

    def __repr__(self):
        if self.debug:
            s = (
                "<REG name: "
                + self.name
                + " reg: "
                + str(self.current)
                + " loaded: "
                + str(self.loaded)
                + " offset: "
                + str(self.offset)
                + " interval:"
                + str(self.start)
                + " -> "
                + str(self.finish)
                + ":"
                + str(self.count)
            )
        else:
            s = "<REG " + self.name + ">"
        return s

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

    def __init__(self, jumper=True):
        self.registers = []
        self.spill = False
        self.free = [R0, R1, R2, R3, R4, R5]
        self.used = []
        self.offset = 1
        if jumper:
            # TODO add in window pointer and jump target
            pass

    def req(self):
        if len(self.free) > 0:
            f = self.free.pop(0)
            self.used.append(f)
            # print("ALLOCATE", f)
            return f
        else:
            # print("RUNOUT")
            raise SpillError()

    def release(self, target, current):
        # release a register
        # TODO move this into the allocator
        instr = []
        # print("target ", target)
        for i in self.registers:
            # don't spill other registers in this command
            if i.current not in current:
                if i.loaded == True:
                    i.loaded = False
                    # a place to spill
                    if i.offset == None:
                        i.offset = self.offset
                        self.offset += 1
                    # the other place to spill
                    if target.offset == None:
                        target.offset = self.offset
                        self.offset += 1
                    # store the reg to spill
                    instr.append(Rem("spill " + i.name))
                    instr.append(opcode.ST(i.current, R6, 8 + i.offset))
                    i.spilt = True
                    # load the new register , or set to zero
                    if target.spilt:
                        instr.append(Rem("load " + target.name))
                        instr.append(opcode.LD(i.current, R6, 8 + target.offset))
                    else:
                        # register is empty , load with a zero
                        instr.append(Rem("zero out " + target.name))
                        instr.append(opcode.MOVI(i.current, 0))
                    # update the target register
                    target.loaded = True
                    target.current = i.current
                    current.append(i.current)
                    # black the old
                    i.current = None
                    break
        return instr

    def display(self, val):
        r = []
        # count = 0
        for i in self.registers:
            r.append(i.within(val))
            # if i.within(val):
            #    count += 1
        return r  # count

    def __getattr__(self, name):
        """ create a new register on access """
        if name not in self.registers:
            new_reg = Register(name, self)
            setattr(self, name, new_reg)
            self.registers.append(new_reg)

        return getattr(self, name)

    def __repr__(self):
        st = ""
        for i in self.registers:
            st += str(i) + "\n"
        return st

    def sort(self):
        newlist = sorted(self.registers, key=lambda x: x.count, reverse=False)
        self.registers = newlist


def reverse_enum(L):
    for index in reversed(range(len(L))):
        yield index, L[index]


class LSRA:
    """Linear Register Allocator """

    # Instruction groups
    INSTRS_BRANCH = {
        BEQ,
        BNE,
        BZ1,
        BZ0,
        BS1,
        BS0,
        BC1,
        BC0,
        BV1,
        BV0,
        BGTS,
        BGTU,
        BGES,
        BLES,
        BLEU,
        BLTS,
    }
    INSTRS_RSD_SOURCE = {ST, STR, STX, STXA}
    INSTRS_JUMP = {J, JAL, JR, JRAL, JST, JVT}

    def __init__(self, window, code):
        self.window = window
        self.code = code
        self.mapper = {}
        self.blocks = []
        self.block_count = 0
        self.current_block = BasicBlock()

    def scan(self):
        """
        LinearScanRegisterAllocation
        active ←{}
        foreach live interval i, in order of increasing start point
            ExpireOldIntervals(i)
            if length(active) = R then
                SpillAtInterval(i)
            else
                register[i] ← a register removed from pool of free registers
                add i to active, sorted by increasing end point
        """
        pass

    def expire(self, interval):
        """ExpireOldIntervals(i)
            foreach interval j in active, in order of increasing end point
                if endpoint[j] ≥ startpoint[i] then
                    return
                remove j from active
                add register[j] to pool of free registers
        """
        pass

    def spill(self, interval):
        """
            SpillAtInterval(i)
            spill ← last interval in active
            if endpoint[spill] > endpoint[i] then
                register[i] ← register[spill]
                location[spill] ← new stack location
                remove spill from active
                add i to active, sorted by increasing end point
            else
                location[i] ← new stack location
        """
        pass

    def intervals(self):
        # Forward Scan
        for i, j in enumerate(self.code):
            if hasattr(j, "_fields"):
                for k in j._fields:
                    # Check all the registers
                    val = getattr(j, k)
                    if isinstance(val, Register):
                        val.count += 1
                        if val.start is None:
                            val.start = i
        # Reverse Scan
        for i, j in reverse_enum(self.code):
            if hasattr(j, "_fields"):
                for k in j._fields:
                    # Check all the registers
                    val = getattr(j, k)
                    if isinstance(val, Register):
                        if val.finish is None:
                            val.finish = i

    def NextBlock(self):
        self.blocks.append(self.current_block)
        self.block_count += 1
        self.current_block = BasicBlock()

    def CreateBasicBlocks(self):
        # need to break into basic blocks
        # map the division points
        for i, j in enumerate(self.code):
            # Find Lables
            if isinstance(j, L):
                # labels are the start of the next block
                self.mapper[i - 1] = (j, 0)
            # Find branches
            for k in self.INSTRS_BRANCH:
                if isinstance(j, k):
                    self.mapper[i] = (j, 1)
            # Find jumps
            for k in self.INSTRS_JUMP:
                if isinstance(j, k):
                    self.mapper[i] = (j, 2)

        # Break into individual blocks
        snipper = list(self.mapper.items())
        snipper.pop(0)
        cur = (0, 0)
        print(snipper)
        for i, j in enumerate(self.code):
            self.current_block.add((i, j))
            if i == cur[0]:
                print("new block")
                if len(snipper) == 0:
                    continue
                cur = snipper.pop(0)
                self.NextBlock()
            # print("-->", i, j, cur, snipper)
        # and attach the last block
        self.NextBlock()
        # Attach all the registers used in block
        for i in self.blocks:
            i.GetReg()

    def show(self):
        for i, j in enumerate(self.blocks):
            print(i)
            print(j.code)
            print(j.registers)

    def show_counts(self):
        for i, j in enumerate(self.code):
            val = self.window.display(i)
            if val > self.window.max:
                print("----UH OH-----")
            print(val, j)

    def run(self):
        self.intervals()
        self.CreateBasicBlocks()
        print(self.mapper)


def expand(code):
    # expand the code
    # stoopid useless allocator
    new_code = []
    for i, j in enumerate(code):
        if isinstance(j, Wrapper):
            new_code.append(j.allocate())
        else:
            new_code.append(j)
    return new_code


if __name__ == "__main__":
    o = other["OR"]
    m = other["MOVI"]
    mr = other["MOVR"]
    s = other["STXA"]
    w = Window()
    # random code test
    v = [
        MOVI(w.counter, 0),
        L("wait"),
        ADDI(w.counter, w.counter, 1),
        CMPI(w.counter, 0xFFFF),
        BNE("wait"),
        m(w.target, 0xFFFF),
        m(w.a, 4),
        m(w.b, 5),
        m(w.c, 7),
        m(w.d, 8),
        m(w.e, 5),
        CMPI(w.e, 100),
        BNE("main"),
        m(w.target, 0x0FFF),
        m(w.f, 7),
        m(w.g, 8),
        m(w.h, 9),
        m(w.i, 10),
        CMPI(w.i, 40),
        BEQ("main"),
        m(w.target, 0xF0FF),
        m(w.j, 11),
        m(w.k, 12),
        o(w.a, w.b, w.c),
        s(w.target, 10),
        MOVI(w.counter, 100),
        L("again"),
        SUBI(w.counter, w.counter, 1),
        AND(w.target, w.target, w.counter),
        CMPI(w.counter, 0),
        BNE("again"),
        JAL(w.bork, "main"),
        STXA(w.stuff, 1),
        MOVI(w.a, 4),
        MOVI(w.h, 3),
        MOVI(w.g, 4),
    ]
    # print("INPUT")
    # print(v)
    # pp  = preproc(v)
    # print("OUTPUT")
    # print(pp)
    # d = Instr.assemble(pp)
    # print(d)
    # print(Instr.disassemble(d))
    l = LSRA(w, v)
    l.run()
    l.show()

    # i = expand(v)
    # w.sort()

    # print(i)
    print(str(w))
