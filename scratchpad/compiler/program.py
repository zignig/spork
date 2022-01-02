# the basic program construct

from .base import Base
from .defn import Defn
from .vartypes import *
class Program(Defn):
    def __init__(self, program):
        # extract this into setup
        for i in type_list:
            self._symbols.add(i.name,i)
        self._symbols.add("print", "")
        self.name = "program"
        self.body = program


class task(Defn):
    def __init__(self, name, body):
        self.name = name
        self.body = body
        self.tasks.append(self)
