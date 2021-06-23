# An upwards searching symbol table
# Used all the way through the compiler


class SymbolTable:
    def __init__(self, parent=None, name="anon"):
        self.symbols = {}
        # for nested tables
        self.children = []
        self.parent = parent
        self.name = name
        self._empty = True
        if self.parent is not None:
            if isinstance(parent, SymbolTable):
                parent.children.append(self)
            else:
                raise BaseException("Not a symbol table")

    def add(self, name, value):
        self._empty = False
        print("adding -> ", name, value, " to ", self.name)
        if name in self.symbols:
            print(self)
            raise BaseException("symbol already exists %s" % name)
        self.symbols[name] = value

    def get(self, name):
        print("searching for ", name, " in ", self.name)
        if name in self.symbols:
            print("\tfound ", name, " in ", self.name)
            return self.symbols[name]
        # search up the scopes
        if self.parent is not None:
            print("up ->", self.parent.name)
            return self.parent.get(name)
        # no symbol at this point
        print(">", name, "< not found in")
        print(self)
        raise BaseException("no symbol found >%s<" % name)

    def __repr__(self):
        lines = []
        # lines.append("Symbol Table for %s" % (self.name))
        if self.parent is not None:
            lines.append("%s >> %s" % (self.parent.name, self.name))
        else:
            lines.append(self.name)
        for key, value in self.symbols.items():
            lines.append("|%7s|: %20r |" % (key, value))
        # lines.append("\n")
        if len(self.children) > 0:
            for i in self.children:
                if not i._empty:
                    lines.append(i.__repr__())
