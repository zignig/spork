# Walk to generate the symbol table


from .visitor import NodeVisitor
from .base import SymbolTable
from .base import Base
from .vartypes import *

# Generates the symbol table
# and attaches local_symbols to the nodes that need it
class GenSymbols(NodeVisitor):
    def visit_Program(self, node):
        for i in node.body:
            self.visit(i)

    def show(self):
        pass

    def visit_func(self, node):
        # add a new name space
        node.add_sym(node.name.name, node)
        node.add_namespace(node.name.name)
        self.visit(node.params)
        for i in node.body:
            self.visit(i)
        node.pop_namespace()

    def visit_declparam(self, node):
        for i in node.params:
            self.visit(i)

    def visit_const(self, node):
        node.add_sym(node.name.name, node)

    def visit_dvar(self, node):
        node.add_sym(node.name, node)
        node.local_symbols = Base._current

    def _visit_returner(self, node):
        pass

    def visit_var(self, node):
        self.visit(node.name)
        node.local_symbols = Base._current

    def visit_ident(self, node):
        node.local_symbols = Base._current

    def visit_use(self, node):
        for i in node.includes:
            node.add_sym(i.name, i)

    def visit_call(self, node):
        # so the call can look up labels
        node.local_symbols = Base._current
        for i in node.params:
            self.visit(i)

    def visit_stringer(self, node):
        print("add stringer")

    def visit_param(self, node):
        print("PARAMS")
        node.detail()

    def visit_returner(self, node):
        self.visit(node.expr)

    def visit_number(self, node):
        pass

    def visit_comment(self, node):
        pass

    def visit_assign(self, node):
        self.visit(node.lhs)
        self.visit(node.rhs)

    def visit_whiler(self, node):
        self.visit(node.expr)
        for i in node.body:
            self.visit(i)

    def visit_evaluate(self, node):
        self.visit(node.comp)

    def visit_compare(self, node):
        self.visit(node.rhs)
        self.visit(node.lhs)

    def visit_iffer(self, node):
        self.visit(node.expr)
        for i in node.body:
            self.visit(i)

    def visit_variable(self, node):
        node.add_sym(node.name.name, node)
        node.local_symbols = Base._current
        if node.setvar is not None:
            self.visit(node.setvar)

    def visit_setvar(self, node):
        self.visit(node.expr)

    def visit_struct(self, node):
        node.add_sym(node.name.name, node)
        node.add_namespace(node.name.name)
        for i in node.body:
            self.visit(i)
        node.pop_namespace()

    def binop(self, node):
        self.visit(node.rhs)
        self.visit(node.lhs)

    def visit_add(self, node):
        self.binop(node)

    def visit_sub(self, node):
        self.binop(node)

    def visit_modulus(self, node):
        self.binop(node)
