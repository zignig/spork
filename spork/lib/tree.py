#  tree test

from ..firmware.base import *
from .stringer import Stringer

from boneless.arch.opcode import Instr
from boneless.arch.opcode import *

from rich import print

from spork.firmware.base import *
from spork.lib.uartIO import UART

from spork.logger import logger

log = logger(__name__)

# get a uart interface
u = UART()
ws = u.writestring  # write a char
sp = u.sp  # write a space
cr = u.cr
ho = u.writeHex


class ShowMenu(SubR):
    """ 
    The addressing of the pointer are annoying
    because they are relative pointers that may or may not
    be negative
    """

    params = ["address", "depth"]
    locals = ["children", "pointer", "temp", "offfset"]

    def setup(self):
        log.critical("OFFSETS may be bad")

    def instr(self):
        w = self.w
        ll = LocalLabels()
        return [
            LD(w.pointer, w.address, 0),
            Rem("Addresses are relative offsets that may be -ve"),
            Rem("drop the high bit"),
            # ANDI(w.temp, w.pointer, 0x8000 - 1),
            # ho(w.temp),cr(),
            SUB(w.pointer, w.address, w.pointer),
            LD(w.children, w.address, 1),
            MOV(w.temp, w.depth),
            # ho(w.address),cr(),
            # ho(w.pointer),cr(),
            ll("depth_loop"),
            sp(),
            SUBI(w.temp, w.temp, 1),
            CMPI(w.temp, 0),
            BGES(ll.depth_loop),
            Rem("Output the name"),
            ws(w.pointer),
            cr(),
            CMPI(w.children, 0),
            BEQ(ll.no_children),
            # ho(w.children),cr(),
            Rem("copy and increment depth"),
            MOV(w.temp, w.depth),
            ADDI(w.temp, w.temp, 2),
            Rem("Adjust the address to point to the first child"),
            ADDI(w.address, w.address, 1),
            ll("child_loop"),
            ADDI(w.address, w.address, 1),
            LD(w.pointer, w.address, 0),
            Rem("pointers here are positive WTF?"),
            ADD(w.pointer, w.address, w.pointer),
            Rem("Recursive Call"),
            # ho(w.pointer),
            # cr(),cr(),
            self(w.pointer, w.temp),
            Rem("Loop through the children"),
            SUBI(w.children, w.children, 1),
            CMPI(w.children, 0),
            BNE(ll.child_loop),
            ll("no_children"),
        ]


class Menu(CodeObject):
    "Structured Data tree"
    _stringer = Stringer()
    _ref = LocalLabels()
    _counter = 0

    def __init__(self, name, item=None, parent=None):
        self.parent = parent
        # log.critical("{} {}".format(name, parent))
        if parent == None:
            log.debug("Attach root of tree")
            super().__init__()
        self.name = name
        self.item = item
        self.children = []
        self.label = self.new_label(name)
        self.stringlabel = self._stringer.add(name, name)
        self.stringlabel._used = True
        self.flat = []

    def __call__(self, register):
        self._used = True
        return [MOVR(register, self.label)]

    def new_label(self, name):
        l = Menu._ref.set(str(name) + "_" + str(Menu._counter))
        Menu._counter += 1
        return l

    def add(self, name, item=None):
        val = Menu(name, item, parent=self)
        # val.parent = self
        self.children.append(val)
        return val

    def digest(self, menu_as_dict):
        pass

    def show(self, depth=0):
        print(">>" + 2 * depth * " " + self.name)
        depth = depth + 1
        if len(self.children) > 0:
            for i in self.children:
                i.show(depth)

    def flatten(self):
        # collect strings
        names = [self]
        if len(self.children) > 0:
            for i in self.children:
                names += i.flatten()
        return names

    def code(self):
        l = []
        self.flat = self.flatten()
        self._stringer.all()
        for i in self.flat:
            l += [Rem("-----")]
            l += [[Rem(i.name), L(i.label)]]
            l += [Ref(i.stringlabel.get_name())]
            l += [len(i.children)]
            # l += [Ref(i.item)]
            for j in i.children:
                l.append(Ref(j.label))
        return l


if __name__ == "__main__":
    m = Menu("base")
    one = m.add("one", None)
    one.add("three", None)
    one.add("four", None)
    three = one.add("five", None)
    three.add("asdfasdf", None)
    three.add("fnord", None)
    under = three.add("three", None)
    under.add("base")
    under.add("base")
    under.add("base")

    m.add("under", None)
    m.show()
    print(m(R0))
    n = [m.code(), m._stringer.code()]
    print(n)
    s = ShowMenu()
    print(s.code())
