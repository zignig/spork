# Walk the ast and do some syntax checking

from .visitor import NodeVisitor

class SyntaxCheck(NodeVisitor):

    def visit_Program(self,node):
        for i in node.body:
            self.visit(i)

    def visit_func(self,node):
        self.visit(node.params)
        for i in node.body:
            self.visit(i)

    def visit_comment(self,node): pass

    def visit_const(self,node): pass # const def generates no code (GNC)
    
    def visit_variable(self,node):
        # check that the variable exists
        node.local_symbols.get(node.name.name)
        # check that the type exisits
        node.local_symbols.get(node.vtype)
    
    def visit_declparam(self,node):
        for i in node.params:
            self.visit(i)

    def visit_dvar(self,node):
        node.local_symbols.get(node.vtype)
        node.local_symbols.get(node.name)
    # and the rest
