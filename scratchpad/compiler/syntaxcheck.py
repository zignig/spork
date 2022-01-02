# Walk the ast and do some syntax checking

from .visitor import NodeVisitor


class TypeError(Exception):
    def __init__(self, nodea, nodeb, code):
        print("Type Error")
        line = nodeb.meta.line - 1
        col = nodeb.meta.column - 1
        info = code[line]
        print("Error on line " + str(line) + " column " + str(col))
        for i, j in enumerate(code[line - 2 : line + 2]):
            print("{:04d}".format(i + line), ":", j)
            if i + line == line + 2:
                print(" " * (col + 7) + "^ are incompatible types")
        print(str(nodea) + " and " + str(nodeb))


def compare_types(nodea, nodeb, code):
    if nodea.ctype == nodeb.ctype:
        return True
    else:
        raise TypeError(nodea, nodeb, code)


class SyntaxCheck(NodeVisitor):
    def __init__(self, code=None, display=False):
        self._display = display
        # for errors
        self.code = code

    def show(self):
        pass

    def visit_Program(self, node):
        for i in node.body:
            self.visit(i)

    def visit_func(self, node):
        self.visit(node.params)
        for i in node.body:
            self.visit(i)

    def visit_comment(self, node):
        pass

    def visit_const(self, node):
        pass  # const def generates no code (GNC)

    def visit_variable(self, node):
        # check that the variable exists
        node.local_symbols.get(node.name.name)
        # check that the type exisits
        node.ctype = node.local_symbols.get(node.vtype)
        if node.ctype is None:
            raise BaseException("BORK")
        if node.setvar is not None:
            self.visit(node.setvar)

    def visit_setvar(self, node):
        self.visit(node.expr)

    def visit_declparam(self, node):
        for i in node.params:
            self.visit(i)

    def visit_dvar(self, node):
        "get the concrete type"
        node.ctype = node.local_symbols.get(node.vtype)
        node.local_symbols.get(node.name)

    def visit_call(self, node):
        for i in node.params:
            self.visit(i)

    def visit_param(self, node):
        for i in node.params:
            self.visit(i)

    def visit_stringer(self, node):
        pass

    def visit_returner(self, node):
        self.visit(node.expr)

    def visit_var(self, node):
        ref = node.local_symbols.get(node.name.name)
        node.ctype = ref.ctype

    def visit_iffer(self, node):
        self.visit(node.expr)
        for i in node.body:
            self.visit(i)

    def visit_whiler(self, node):
        self.visit(node.expr)
        for i in node.body:
            self.visit(i)

    def visit_evaluate(self, node):
        self.visit(node.comp)

    def visit_compare(self, node):
        self.visit(node.rhs)
        self.visit(node.lhs)

    def visit_number(self, node):
        pass

    def visit_assign(self, node):
        self.visit(node.rhs)
        self.visit(node.lhs)
        if compare_types(node.lhs, node.rhs, self.code):
            node.ctype = node.rhs.ctype

    def visit_ident(self, node):
        ref = node.local_symbols.get(node.name)
        node.ctype = ref.ctype

    def binop(self, node):
        self.visit(node.rhs)
        self.visit(node.lhs)
        if compare_types(node.lhs, node.rhs, self.code):
            node.ctype = node.lhs.ctype

    def visit_modulus(self, node):
        return self.binop(node)

    def visit_add(self, node):
        return self.binop(node)

    # and the rest
