# compiler identitys , numbers parameters and enumerations

from .named import Named


class declparam(Named):
    def __init__(self, *tree):
        # print(self,tree)
        self.params = tree

    def process(self, instr):
        for i in self.params:
            i.process(instr)


class ident(Named):
    def __init__(self, name, *dotted):
        self.name = name
        self.dotted = dotted

    def process(self, instr):
        pass


class param(Named):
    def __init__(self, *tree):
        print(self, tree)
        self.params = tree

    def process(self, instr):
        self.current.parent.add(self.name.name, self)
        pass
