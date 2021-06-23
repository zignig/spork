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

    def process(self, instr):
        instr.append("program setup")
