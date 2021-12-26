# calls, structs and fields

from .base import Base
from .named import Named


class fields(Named):
    def __init__(self, *tree):
        self.fields = tree


class dvar(Base):
    def __init__(self, vtype, ident):
        self.vtype = vtype
        self.name = ident.name

class call(Base):
    def __init__(self, name, params):
        self.name = name.name
        self.params = params
        self.body = None


class comment(Base):
    pass
