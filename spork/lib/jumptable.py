
"""

Jump table construct 

used to run code base on enumeration 

get jump ref as an integer

guard the integer size
- table 
ref1
ref2
ref3

ref1:
 code
 code 
 code
 J(end)

ref2:
 code
 code 
 code
 J(end)

end:

"""

from ..firmware.base import *
from ..logger import logger


from boneless.arch.opcode import Instr
from boneless.arch.opcode import *

from enum import IntEnum, auto

log = logger(__name__)


class TestEnum(IntEnum):
    one = auto()
    two = auto()
    three = auto()
    four = auto()
    other = auto()
    fnord = auto()


class JumpEntry:
    def __init__(self, name, tag):
        self._active = False
        self.tag = tag
        self.name = name
        self.instr = []

    def __repr__(self):
        st = str(self._active) + "\n"
        st += str(self.tag) + "\n"
        st += str(self.instr) + "\n"
        return st

    def set(self, tag, postfix, code):
        self.tag = tag + postfix
        self.instr = code
        self._active = True

    def entry(self):
        return [Rem(self.name), Ref(self.tag)]

    def code(self):
        if self._active:
            return [L(self.tag), self.instr]
        return None


class JumpTable:
    """
     The jump table takes a bounded integer and runs that code
    
    enumer : a list of integers to bind

    """

    def __init__(self, enumer):
        self.items = []
        self.labels = LocalLabels()
        self.labels("unbound")
        self.labels("exit")
        if type(enumer) is not type(IntEnum):
            raise ("Not an enumeration")
        self.length = len(enumer)
        for i in enumer:
            self.items.append(JumpEntry(i, self.labels.unbound))

    def add(self, item):
        if isinstance(item, list):
            for i in item:
                self.add(i)
        else:
            if len(item) != 2:
                raise FWError()
            code = item[1]
            self.items[item[0] - 1].set(str(item[0]), self.labels._postfix, code)

    def __repr__(self):
        s = ""
        s += str(self.items)
        return s

    def __call__(self, reg):
        jump_list = []
        code_list = []
        for i in self.items:
            jump_list.append(i.entry())
            code = i.code()
            if code is not None:
                code_list.append([i.code(), J(self.labels.exit)])

        return [
            Rem("Jump vector table"),
            JVT(reg, self.labels.vector_start),
            self.labels("vector_start"),
            jump_list,
            Rem("End vector table"),
            code_list,
            self.labels("unbound"),
            L(self.labels.exit),
        ]


if __name__ == "__main__":
    import pprint
    from .action_list import EscKeys

    log.critical("JUMP TABLE")
    jt = JumpTable(EscKeys)
    jt.add([(EscKeys.F1, [Rem("hello")]), (EscKeys.BS, [MOVI(R0, 0xFFFF)])])
    pprint.pprint(jt(R0))
