# structural objects

from .base import Base, SymbolTable
from .defn import Defn


class use(Base):
    def __init__(self,*includes):
        self.includes = includes


class evaluate(Base):
    def __init__(self,lhs,op,rhs):
        self.lhs = lhs
        self.op = op
        self.rhs = rhs

class proc(Defn):
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body


class impl(Defn):
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body


class func(Defn):
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body

class on_event(Defn):
    def __init__(self, name, body):
        self.name = name
        self.body = body


class task(Defn):
    def __init__(self, name, body):
        self.name = name
        self.body = body

class returner(Base):
    pass
