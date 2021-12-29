from .base import Base

class Compare(Base):
    def __init__(self,meta):    
        self.meta = meta 

class compare(Base):
    def __init__(self,meta,lhs,op,rhs):
        self.meta = meta 
        self.lhs = lhs
        self.op = op
        self.rhs = rhs
        

class lt(Compare):
    sym = "<"
    instr = "BLTU"


class gt(Compare):
    sym = ">"
    instr = "BLTU"


class lte(Compare):
    sym = "<="  


class gte(Compare):
    sym = ">="


class eq(Compare):
    sym = "=="
    instr = "BEQ"


class neq(Compare):
    sym = "!="
