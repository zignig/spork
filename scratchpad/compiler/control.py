# all the control structures

from .defn import Defn


class iffer(Defn):
    def __init__(self, expr, body, elser=None):
        self.expr = expr
        self.body = body
        self.elser = elser


class whiler(Defn):
    def __init__(self, expr, body):
        self.expr = expr
        self.body = body
