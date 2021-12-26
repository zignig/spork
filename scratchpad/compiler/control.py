# all the control structures

from .defn import Defn


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

    def scan(self, instr, fn):
        self.expr.scan(instr, fn)
        for item in self.body:
            item.scan(instr, fn)

