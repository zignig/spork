# compiler identitys , numbers parameters and enumerations

from .named import Named


class declparam(Named):
    def __init__(self, *tree):
        # print(self,tree)
        self.params = tree


class ident(Named):
    def __init__(self, name, *dotted):
        self.name = name
        self.dotted = dotted


class param(Named):
    def __init__(self, *tree):
        print(self, tree)
        self.params = tree
