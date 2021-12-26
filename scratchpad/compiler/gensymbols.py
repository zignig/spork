# Walk to generate the symbol table 


from .visitor import NodeVisitor
from .base import SymbolTable
from .base import Base 

class GenSymbols(NodeVisitor):

    def visit_Program(self,node):
        for i in node.body:
            self.visit(i)

    def visit_func(self,node):
        # add a new name space
        node.add_sym(node.name.name,node)
        node.add_namespace(node.name.name)
        self.visit(node.params)
        for i in node.body:
            self.visit(i)
        node.pop_namespace()

    def visit_declparam(self,node):
        for i in node.params:
            self.visit(i)
        
    def visit_dvar(self,node):
        node.add_sym(node.name,node)

    def visit_returner(self,node):
        pass

    def visit_call(self,node): pass
    def visit_comment(self,node): pass

    def visit_assign(self,node): pass

    def visit_whiler(self,node):
        for i in node.body:
            self.visit(i)

    def visit_variable(self,node):
        node.add_sym(node.name.name,node)