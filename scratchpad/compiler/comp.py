from .base import Base


class compare(Base):
    def __init__(self,meta):
        self.meta = meta 
        

class lt(compare):
    sym = "<"


class gt(compare):
    sym = ">"


class lte(compare):
    sym = "<="  


class gte(compare):
    sym = ">="


class eq(compare):
    sym = "=="


class neq(compare):
    sym = "!="
