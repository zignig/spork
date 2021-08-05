from .base import Base


class compare(Base):
    def __init__(self, lhs, comp, rhs):
        self.lhs = lhs
        self.comp = comp
        self.rhs = rhs


class Compare(Base):
    def __init__(self):
        pass


class lt(Compare):
    pass


class gt(Compare):
    pass


class lte(Compare):
    pass


class gte(Compare):
    pass


class eq(Compare):
    pass


class neq(Compare):
    pass
