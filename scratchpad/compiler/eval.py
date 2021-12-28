# structural evaluation
# basic arithmatic and variable stuff

# basic arith
# convert to tripples

from .base import Base
from .named import Named
from .defn import Defn


class assign(Base):
    def __init__(self,meta, lhs, rhs):
        self.meta = meta
        self.name = lhs
        self.lhs = lhs
        self.rhs = rhs

class const(Base):
    def __init__(self,meta,vtype, name,setvar=None):
        self.meta = meta
        self.name = name
        self.vtype = vtype
        self.setvar = setvar
        
class variable(Base):
    def __init__(self, meta , vtype, name, setvar=None):
        self.meta = meta
        self.name = name
        self.vtype = vtype

class setvar(Base):
    def __init__(self,meta,expr):
        self.meta = meta
        self.expr = expr

class var(Named):
    def __init__(self,meta,name):   
        self.meta = meta 
        self.name = name
        
class Arith(Base):
    def __init__(self,meta,lhs, rhs):
        self.meta = meta
        self.lhs = lhs
        self.rhs = rhs
        self.target = None

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
