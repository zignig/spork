#  tree test

from ..firmware.base import *
from .stringer import Stringer

from boneless.arch.opcode import Instr
from boneless.arch.opcode import *

from rich import print


class menu:
    _stringer = Stringer()
    _ref = LocalLabels()
    _counter = 0

    def __init__(self, name, item=None):
        self.name = name
        self.item = item
        self.parent = None
        self.children = []
        self.label = self.new_label(name)
        self.stringlabel = self._stringer.add(name, name)
        self.flat = []

    def new_label(self, name):
        l = menu._ref.set(str(name) + "_" + str(menu._counter))
        menu._counter += 1
        return l

    def add(self, name, item=None):
        val = menu(name, item)
        val.parent = self
        self.children.append(val)
        return val

    def digest(self, menu_as_dict):
        pass

    def show(self, depth=0):
        print(2 * depth * " " + self.name)
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

    def dump(self):
        l = []
        self.flat = self.flatten()
        for i in self.flat:
            l += [Rem("-----")]
            l += [[Rem(i.name), L(i.label)]]
            l += [[Rem("str"), Ref(i.stringlabel.get_name())]]
            l += [len(i.children)]
            for j in i.children:
                l.append(Ref(j.label))
        print(Rem("strings"))
        self._stringer.all()
        l += self._stringer.get_code()
        return l


if __name__ == "__main__":
    m = menu("base")
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
    n = m.dump()
    print(n)
