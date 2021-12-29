# calls, structs and fields

from .base import Base
from .named import Named


class fields(Named):
    def __init__(self,meta, *tree):
        self.meta = meta
        self.fields = tree


class dvar(Base):
    def __init__(self,meta,vtype, ident):
        self.meta = meta
        self.vtype = vtype
        self.name = ident.name

class call(Base):
    def __init__(self,meta, name, params):
        self.meta = meta
        self.name = name.name
        self.params = params
        self.body = None


class comment(Base):
    def __init__(self,meta,val):
        self.name = 'comment'
        self.meta = meta
        self.val = val
