# structural objects

from .base import Base, SymbolTable
from .defn import Defn


class returner(Base):
    def process(self, instr):
        instr.append(self)


# `class body(Defn):
# `   def __init__(self, *body):
# `      print(body)
# `     self.body = body


class use(Base):
    pass


class proc(Defn):
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body


class impl(Defn):
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body
        self.impl.append(self)


class func(Defn):
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body
        self.functions.append(self)

    def process(self, instr):
        # add the fuction to the table above
        self.current.parent.add(self.name.name, self)
        self.params.process(instr)
        instr.append("function setup %s" % (self.name.name))
        self.proc_body(instr)
        instr.append("return values")


class on_event(Defn):
    def __init__(self, name, body):
        self.name = name
        self.body = body


class task(Defn):
    def __init__(self, name, body):
        self.name = name
        self.body = body
        self.tasks.append(self)

    def process(self, instr):
        # add the fuction to the table above
        print("add task")
        self.current.parent.add(self.name.name, self)
