# Walk the ast and do some syntax checking

from .visitor import NodeVisitor


def compare_types(nodea,nodeb):
        if nodea.ctype == nodeb.ctype:
            return True
        else:
            print(nodea,nodeb)
            raise BaseException(nodea.meta.line)

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
        node.ctype = node.local_symbols.get(node.vtype)
        if node.setvar is not None:
            self.visit(node.setvar)
    
    def visit_setvar(self,node):
        self.visit(node.expr)

    def visit_declparam(self,node):
        for i in node.params:
            self.visit(i)

    def visit_dvar(self,node):
        "get the concrete type"
        node.ctype = node.local_symbols.get(node.vtype)
        node.local_symbols.get(node.name)

    def visit_call(self,node):
        self.visit(node.params)

    def visit_param(self,node): 
        for i in node.params:
            self.visit(i)

    def visit_returner(self,node):      
        self.visit(node.expr)

    def visit_var(self,node):
        ref = node.local_symbols.get(node.name.name)
        node.ctype = ref.ctype

    def visit_whiler(self,node):
        self.visit(node.expr)

    def visit_evaluate(self,node):
        self.visit(node.comp)

    def visit_compare(self,node):
        self.visit(node.rhs)
        self.visit(node.lhs)
        
    def visit_number(self,node):
        node.ctype = None

    def visit_assign(self,node):
        self.visit(node.rhs)
        self.visit(node.lhs)
        if compare_types(node.lhs,node.rhs):
            node.ctype = node.lhs.ctype

    def visit_ident(self,node):
        ref = node.local_symbols.get(node.name)
        node.ctype = ref.ctype

    def binop(self,node):
        self.visit(node.rhs)
        self.visit(node.lhs)
        if compare_types(node.lhs,node.rhs):
            node.ctype = node.lhs.ctype
        
    def visit_add(self,node): return self.binop(node)
    # and the rest
