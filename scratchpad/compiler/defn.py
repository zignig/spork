# Definition
# a program section that defines a block

from .base import Base, SymbolTable


class Defn(Base):
    def walk(self, instr):
        print("defn walk")
        print(self.current)
        new_symbol_table = SymbolTable(parent=self.current, name=self.name)
        Base.current = new_symbol_table
        self.process(instr)
        Base.current = Base.current.parent
        print(self.current)

    def scan(self, instr, fn):
        for item in self.body:
            try:
                item.scan(instr, fn)
            except:
                instr += [self]

    def process(self, instr):
        inst = []
        for i in self.body:
            print("body>>", i)
            instr += [i]
            i.process(inst)
        instr += inst
