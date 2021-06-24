# Definition
# a program section that defines a block

from .base import Base
from .symbol import SymbolTable


class Defn(Base):
    def walk(self, instr):
        new_symbol_table = SymbolTable(parent=self.current, name=self.name)
        Base.current = new_symbol_table
        self.process(instr)
        for i in self.body:
            if isinstance(i, Base):
                i.walk(instr)
            else:
                raise BaseException("no bound class", i)
        Base.current = Base.current.parent

    def scan(self, pre=None, post=None):
        # like walk but for code gen
        if pre is not None:
            yield pre(self)
        for s in self.body:
            yield from s.scan(pre, post)
        if post is not None:
            yield post(self)
