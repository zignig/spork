# the basic program construct

from .defn import Defn


class Program(Defn):
    def __init__(self, program):
        # extract this into setup
        self.symbols.add("int", "")
        self.symbols.add("char", "")
        self.symbols.add("bool", "")
        self.symbols.add("string", "")
        self.symbols.add("print", "")
        self.name = "program"
        self.body = program


class task(Defn):
    def __init__(self, name, body):
        self.name = name
        self.body = body
        self.tasks.append(self)

    def process(self, instr):
        self.current.parent.add(self.name.name, self)
