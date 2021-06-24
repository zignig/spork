# The base object for all the compiler objects

from .symbol import SymbolTable


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

    def process(self, instr):
        print("fail , ", self)
