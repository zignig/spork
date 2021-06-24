class use(Base):
    def __init__(self, name):
        self.name = name
        print("include ", name)


class TempVar(Base):
    count = 0

    def __init__(self):
        self.name = "__T" + str(TempVar.count)
        TempVar.count += 1
