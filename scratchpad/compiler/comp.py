from .base import Base


class compare(Base):
    def __init__(self,meta):
        self.meta = meta 
        

class lt(compare):
    pass


class gt(compare):
    pass


class lte(compare):
    pass


class gte(compare):
    pass


class eq(compare):
    pass


class neq(compare):
    pass
