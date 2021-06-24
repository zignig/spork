# calls, structs and fields

from .base import Base
from .named import Named


class fields(Named):
    def __init__(self, *tree):
        self.fields = tree

    def process(self, instr):
        pass


class dvar(Base):
    def __init__(self, vtype, ident):
        self.vtype = vtype
        self.name = ident.name

    def process(self, instr):
        self.current.add(self.name, self)


class call(Base):
    def __init__(self, name, params):
        self.name = name.name
        self.params = params
        self.body = None

    def process(self, instr):
        print("call : ", self.name)
        val = self.current.get(self.name)
        print(val)


class comment(Base):
    pass
