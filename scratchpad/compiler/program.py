# the basic program construct

from .base import Base
from .defn import Defn


class Program(Defn):
    def __init__(self, program):
        # extract this into setup
        self.symbols.add("int", "")
        self.symbols.add("uint", "")
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
