from .base import Base


class use(Base):
    def __init__(self, meta, name):
        self.meta = meta
        self.name = name
        print("include ", name)


class TempVar(Base):
    count = 0

    def __init__(self):
        self.name = "__T" + str(TempVar.count)
        TempVar.count += 1
