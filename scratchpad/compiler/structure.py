# structural objects

from .base import Base, SymbolTable
from .defn import Defn


class use(Base):
    def __init__(self,meta,*includes):
        self.meta= meta
        self.includes = includes


class evaluate(Base):
    def __init__(self,meta,comp):
        self.meta = meta
        self.comp = comp 

class proc(Defn):
    def __init__(self,meta, name, params, body):
        self.meta = meta 
        self.name = name
        self.params = params
        self.body = body


class impl(Defn):
    def __init__(self,meta, name, params, body):
        self.meta = meta
        self.name = name
        self.params = params
        self.body = body


class func(Defn):
    def __init__(self,meta,  name, params, body):
        self.meta = meta
        self.name = name
        self.params = params
        self.body = body

class on_event(Defn):
    def __init__(self, meta, name, body):
        self.meta = meta 
        self.name = name
        self.body = body


class task(Defn):
    def __init__(self,meta, name, body):
        self.meta = meta 
        self.name = name
        self.body = body

class returner(Base):
    def __init__(self,meta,expr):
        self.meta = meta 
        self.expr = expr
