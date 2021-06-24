# structural evaluation
# basic arithmatic and variable stuff

# basic arith
# convert to tripples

from .base import Base
from .named import Named


class assign(Base):
    def __init__(self, lhs, rhs):
        self.name = lhs
        self.lhs = lhs
        self.rhs = rhs

    def process(self, instr):
        self.rhs.process(instr)
        self.lhs.process(instr)


class variable(Base):
    def __init__(self, vtype, name, setvar=None):
        self.name = name
        self.vtype = vtype

    def process(self, instr):
        # check the type
        # t = self.current.get(self.vtype)
        self.current.add(self.name.name, self)
        pass


class var(Named):
    def process(self, instr):
        instr.append(self)


class Arith(Base):
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs
        self.target = None

    def process(self, instr):
        self.lhs.process(instr)
        self.rhs.process(instr)
        self.target = TempVar()
        self.current.add(self.target.name, self.target)
        instr.append(self)
        # self.lhs = self.target

    def action(self, instr):
        instr.append("_" + self.__class__.__qualname__)

    def __repr__(self):
        return (
            str(self.target)
            + "<- "
            + str(self.lhs)
            + " "
            + self.__class__.__qualname__
            + " "
            + str(self.rhs)
        )


class add(Arith):
    pass


class mul(Arith):
    pass


class div(Arith):
    pass


class sub(Arith):
    pass
