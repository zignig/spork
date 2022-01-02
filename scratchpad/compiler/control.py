# all the control structures

from .defn import Defn


class iffer(Defn):
    def __init__(self, meta, expr, body, elser=None):
        self.meta = meta
        self.expr = expr
        self.body = body
        self.elser = elser


class whiler(Defn):
    def __init__(self, meta, expr, body):
        self.meta = meta
        self.expr = expr
        self.body = body
