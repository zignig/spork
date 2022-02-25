# compiler identitys , numbers parameters and enumerations

from .named import Named


class declparam(Named):
    def __init__(self, meta, *tree):
        self.meta = meta
        self.params = tree


class ident(Named):
    def __init__(self, meta, name, dotted=None):
        self.meta = meta
        self.name = name.value
        self.dotted = dotted


class dotted(Named):
    def __init__(self, meta, name, dotted=None):
        self.meta = meta
        self.name = name
        self.dotted = dotted


class param(Named):
    def __init__(self, meta, *param):
        self.meta = meta
        print("PARAM" + str(param))
        self.param = param
