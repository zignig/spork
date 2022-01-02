# data structures

from .base import Base
from .defn import Defn
from .vartypes import *

class struct(Defn):
    def __init__(self, meta,name, *body):
        self.meta = meta 
        self.name = name
        self.body = body

class index(Base):
    def __init__(self,meta, name, index):
        self.meta = meta 
        self.name = name
        self.index = index

class array(Base):
    def __init__(self,meta, val=0):
        self.meta = meta 
        self.val = val

class number(Base):
    def __init__(self,meta, val=0):
        self.meta = meta
        self.name = 'number'
        self.val = val
        self.vtype = Vint.name
        self.ctype = Vint

class enum(Base):
    def __init__(self,meta, name, values):
        self.meta = meta 
        self.name = name
        self.values = values
