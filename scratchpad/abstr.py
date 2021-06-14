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
        if name in self.symbols:
            raise BaseException("symbol already exists %s" % name)
        self.symbols[name] = value

    def get(self, name):
        print("searching for ", name, " in ", self.name)
        if name in self.symbols:
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
            lines.append("-- parent -> %s" % self.parent.name)
        for key, value in self.symbols.items():
            lines.append(">%7s<: %r" % (key, value))
        lines.append("\n")
        if len(self.children) > 0:
            for i in self.children:
                if not i._empty:
                    lines.append(i.__repr__())
        s = "\n".join(lines)
        return s


def filter(filter_type):
    def f(val):
        if isinstance(val, filter_type):
            return val

    return f


class Base:
    body = None
    name = "anon"
    symbols = SymbolTable(name="global")
    current = symbols
    functions = []
    tasks = []
    variables = []
    include = []

    def __init__(self, tree):
        print("key ", self)
        self.body = tree

    def __repr__(self):
        base = (
            # str(type(self))
            # + "-"
            self.__class__.__qualname__
            + " - "
            + str(self.name)
            + ": "
        )
        if hasattr(self, "params"):
            base += str(self.params)
        return base

    def _indent(self, level, val):
        if self.body is not None:
            for i, j in enumerate(self.body):
                print(level * "\t", i, j)
                level += 1
                j._indent(level, j)
                level -= 1

    def walk(self, instr):
        self.process(instr)

    def scan(self, pre=None, post=None):
        if pre is not None:
            yield pre(self)
        if post is not None:
            yield post(self)

    def start_walk(self):
        instr = []
        self.walk(instr)
        return instr

    def pretty(self):
        self._indent(1, self.body)

    def action(self, instr):
        pass

    def process(self, instr):
        print(self.__class__.__qualname__, " has no processor ", self)


class array(Base):
    def __init__(self, val=0):
        self.val = val


class use(Base):
    def __init__(self, name):
        self.name = name
        print("include ", name)


class comment(Base):
    pass


class Arith(Base):
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs

    def process(self, instr):
        self.lhs.process(instr)
        self.rhs.process(instr)
        self.action(instr)
        print(self.__class__.__qualname__)

    def action(self, instr):
        instr.append("_" + self.__class__.__qualname__)

    def __repr__(self):
        return str(self.lhs) + " " + self.__class__.__qualname__ + " " + str(self.rhs)


class add(Arith):
    pass


class mul(Arith):
    pass


class div(Arith):
    pass


class sub(Arith):
    pass


class Named(Base):
    def __init__(self, name):
        self.name = name


class var(Named):
    def process(self, instr):
        print("check and load the register", self.name)
        # self.current.get(self.name)


class ident(Named):
    def __init__(self, name, *dotted):
        print(name, dotted)
        self.name = name
        self.dotted = dotted


class number(Named):
    def process(self, instr):
        instr.append("MOIV(" + self.name + ")")


class param(Base):
    def __init__(self, *tree):
        self.params = tree

    def process(self, instr):
        print(self.params)


class fields(Base):
    def __init__(self, *tree):
        self.fields = tree

    def process(self, instr):
        print(self.fields)


class call(Base):
    def __init__(self, name, params):
        self.name = name.name
        self.params = params
        self.body = None

    def process(self, instr):
        print("calllmeee")
        val = self.current.get(self.name)
        print(val)


class Defn(Base):
    def walk(self, instr):
        new_symbol_table = SymbolTable(parent=self.current, name=self.name)
        Base.current = new_symbol_table
        self.process(instr)
        for i in self.body:
            if isinstance(i, Base):
                i.walk(instr)
            else:
                raise BaseException("no bound class", i)
        Base.current = Base.current.parent

    def scan(self, pre=None, post=None):
        # like walk but for code gen
        if pre is not None:
            yield pre(self)
        for s in self.body:
            yield from s.scan(pre, post)
        if post is not None:
            yield post(self)


class returner(Base):
    pass


class program(Defn):
    def __init__(self, program):
        # extract this into setup
        self.symbols.add("int", "")
        self.symbols.add("char", "")
        self.symbols.add("bool", "")
        self.symbols.add("string", "")
        self.symbols.add("print", "")
        self.name = "program"
        self.body = program

    def process(self, instr):
        instr.append("program setup")


class struct(Defn):
    def __init__(self, name, *body):
        self.name = name.name
        self.body = body

    def process(self, instr):
        self.current.parent.add(self.name, self)


class task(Defn):
    def __init__(self, name, body):
        self.name = name
        self.body = body
        self.tasks.append(self)

    def process(self, instr):
        # add the fuction to the table above
        print("add task")
        self.current.parent.add(self.name.name, self)


class func(Defn):
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body
        self.functions.append(self)

    def process(self, instr):
        # add the fuction to the table above
        self.current.parent.add(self.name.name, self)
        self.table = self.current.parent
        print(self.params)
        instr.append("function setup %s" % (self.name.name))


class on_event(Defn):
    def __init__(self, name, body):
        self.name = name
        self.body = body


class proc(Defn):
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body


class variable(Base):
    def __init__(self, vtype, name, setvar=None):
        self.name = name
        self.vtype = vtype

    def process(self, instr):
        # check the type
        # t = self.current.get(self.vtype)
        self.current.add(self.name.name, self)


class enum(Base):
    def __init__(self, name, values):
        self.name = name
        self.values = values

    def process(self, instr):
        print(self.name, "--", self.values)


class assign(Base):
    def __init__(self, lhs, rhs):
        self.name = lhs
        self.lhs = lhs
        self.rhs = rhs

    def process(self, instr):
        self.rhs.process(instr)
        self.lhs.process(instr)


class iffer(Base):
    def __init__(self, expr, code, elser=None):
        self.name = "IF"
        self.expr = expr
        self.code = code
        self.elser = elser

    def __repr__(self):
        return str(self.expr) + str(self.body)


class whiler(Base):
    def __init__(self, expr, body):
        self.name = "WHILE"
        self.expr = expr
        self.body = body


class Number(Base):
    def __init__(self, val):
        self.val = val
