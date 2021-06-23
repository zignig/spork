class array(Base):
    def __init__(self, val=0):
        self.val = val


class use(Base):
    def __init__(self, name):
        self.name = name
        print("include ", name)


class comment(Base):
    pass


class TempVar(Base):
    count = 0

    def __init__(self):
        self.name = "__T" + str(TempVar.count)
        TempVar.count += 1


class dvar(Base):
    def __init__(self, vtype, ident):
        self.vtype = vtype
        self.name = ident.name

    def process(self, instr):
        self.current.add(self.name, self)


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


class number(Named):
    def process(self, instr):
        instr.append(self)


class param(Named):
    def __init__(self, *tree):
        print(self, tree)
        self.params = tree

    def process(self, instr):
        self.current.parent.add(self.name.name, self)
        pass


class fields(Named):
    def __init__(self, *tree):
        self.fields = tree

    def process(self, instr):
        pass


class call(Base):
    def __init__(self, name, params):
        self.name = name.name
        self.params = params
        self.body = None

    def process(self, instr):
        print("call : ", self.name)
        val = self.current.get(self.name)
        print(val)


class returner(Base):
    def process(self, instr):
        instr.append(self)


class struct(Defn):
    def __init__(self, name, *body):
        print(name)
        self.name = name
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


class impl(Defn):
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body
        self.impl.append(self)


class func(Defn):
    def __init__(self, name, params, body):
        self.name = name
        print(params)
        self.params = params
        self.body = body
        self.functions.append(self)

    def process(self, instr):
        # add the fuction to the table above
        self.current.parent.add(self.name.name, self)
        self.params.process(instr)
        self.table = self.current.parent
        print(self.params)
        instr.append("function setup %s" % (self.name.name))
        sub = []
        for i in self.body:
            sub.append(i)
        instr.append(sub)


class on_event(Defn):
    def __init__(self, name, body):
        self.name = name
        self.body = body


class proc(Defn):
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body


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


class iffer(Defn):
    def __init__(self, expr, body, elser=None):
        self.name = "IF"
        self.expr = expr
        self.body = body
        self.elser = elser


class whiler(Defn):
    def __init__(self, expr, body):
        self.name = "WHILE"
        self.expr = expr
        self.body = body


class Number(Base):
    def __init__(self, val):
        self.val = val
