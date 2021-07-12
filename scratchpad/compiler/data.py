# data structures

from .base import Base
from .defn import Defn


class struct(Defn):
    def __init__(self, name, *body):
        print(name)
        self.name = name
        self.body = body

    def process(self, instr):
        self.current.parent.add(self.name, self)


class index(Base):
    def __init__(self, name, index):
        self.name = name
        self.index = index


class array(Base):
    def __init__(self, val=0):
        self.val = val


class number(Base):
    def process(self, instr):
        instr += [self]


class enum(Base):
    def __init__(self, name, values):
        self.name = name
        self.values = values
