# The base object for all the compiler objects


# An upwards searching symbol table
# Used all the way through the compiler


class SymbolTable:
    def __init__(self, parent=None, name="anon"):
        print("Create table %s" % name)
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
        lines.append("Symbol Table for %s" % (self.name))
        if self.parent is not None:
            lines.append("%s >> %s" % (self.parent.name, self.name))
        else:
            lines.append(self.name)
        for key, value in self.symbols.items():
            lines.append("|%7s|: %20r |" % (key, value))
        lines.append("\n")
        if len(self.children) > 0:
            for i in self.children:
                if not i._empty:
                    lines.append(i.__repr__())
        s = "\n".join(lines)
        return s


class Base:
    body = None
    name = "anon"
    symbols = SymbolTable(name="global")
    current = symbols
    functions = []
    impl = []
    tasks = []
    variables = []
    include = []

    def __init__(self, tree):
        self.body = tree

    def __repr__(self):
        base = (
            # str(type(self))
            # + "-"
            "("
            + str(self.__class__.__qualname__)
            + " - "
            + str(self.name)
            + ")"
        )
        if hasattr(self, "params"):
            base += " "
            base += str(self.params)
        return base

    def _indent(self, level, val):
        if self.body is not None:
            for i, j in enumerate(self.body):
                print(level * "\t", i, j)
                level += 1
                j._indent(level, j)
                level -= 1

    def proc_body(self, instr):
        body = []
        try:
            for i in self.body:
                i.process(body)
        except:
            body.append(i)
        instr += [body]

    def walk(self, instr):
        print("base walk")
        self.process(instr)

    def scan(self, instr, fn):
        instr += [self]

    def start_walk(self):
        instr = []
        self.walk(instr)
        return instr

    def process(self, instr):
        print("fail , ", self)
