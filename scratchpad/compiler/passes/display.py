# Display the AST
# Just a simple walker


from .visitor import NodeVisitor


class Display(NodeVisitor):
    _display = False

    def __init__(self, display=False):
        self._display = display
        self._data = ""
        self._indent = 0

    def show(self):
        print(self._data)

    def _print(self, value):
        self._data += str(value)

    def _ind(self):
        value = "   " * self._indent
        self._data += value

    def _nl(self):
        self._data += "\n"

    def _body(self, node):
        self._print("){")
        self._nl()
        self._indent += 1
        for i in node.body:
            self._ind()
            self.visit(i)
        self._ind()
        self._print("\n}")
        self._indent -= 1
        self._nl()

    def visit_Program(self, node):
        for i in node.body:
            self.visit(i)

    def visit_func(self, node):
        self._print("func " + node.name.name + "(")
        self.visit(node.params)
        self._body(node)
        self._nl()

    def visit_declparam(self, node):
        for i in node.params[:-1]:
            self.visit(i)
            self._print(",")
        if len(node.params) > 0:
            self.visit(node.params[-1])

    def visit_returner(self, node):
        self._print("return ")
        self.visit(node.expr)

    def visit_setvar(self, node):
        self._print(" = ")
        self.visit(node.expr)

    def visit_whiler(self, node):
        self._print("while( ")
        self.visit(node.expr)
        self._body(node)
        self._nl()

    def visit_iffer(self, node):
        self._print("if( ")
        self.visit(node.expr)
        self._body(node)
        self._nl()

    def visit_const(self, node):
        self._print("const " + node.vtype + " " + node.name.name)
        if node.setvar is not None:
            self.visit(node.setvar)
        self._print("\n")

    def visit_assign(self, node):
        self.visit(node.lhs)
        self._print(" = ")
        self.visit(node.rhs)
        self._print("\n")

    def visit_evaluate(self, node):
        self.visit(node.comp)

    def visit_compare(self, node):
        self.visit(node.lhs)
        self.visit(node.op)
        self.visit(node.rhs)

    def visit_dvar(self, node):
        self._print(node.vtype + " " + node.name)

    def visit_ident(self, node):
        self._print(node.name)
        if node.dotted is not None:
            self.visit(node.dotted)

    def visit_dotted(self, node):
        print("DOTTED")
        print(node.name)
        if node.dotted is not None:
            self.visit(node.dotted)

    def visit_add(self, node):
        self.visit(node.lhs)
        self._print(" + ")
        self.visit(node.rhs)

    def visit_var(self, node):
        self.visit(node.name)

    def visit_number(self, node):
        self._print(node.val)

    def visit_comment(self, node):
        self._print(node.val + "\n")

    def visit_stringer(self, node):
        self._print(node.value)

    def visit_variable(self, node):
        self._print("var ")
        self._print(node.vtype)
        self._print(" ")
        self._print(node.name.name)
        if node.setvar is not None:
            self.visit(node.setvar)
        self._nl()

    def visit_param(self, node):
        node.detail()

    def visit_call(self, node):
        self._print(node.name)
        self._print("(")
        for i in node.params[:-1]:
            self.visit(i)
            self._print(",")
        if len(node.params) > 0:
            self.visit(node.params[-1])
        self._print(")")

    def visit_array(self, node):
        self._print("[")
        self.visit(node.val)
        self._print("]")
        self._print("[")
        self.visit(node.val)

    def visit_index(self, node):
        node.detail()
        self._print(node.name.name)
        self._print("[")
        self.visit(node.value)
        self._print("]")

    def visit_int(self, node):
        self._print(node)

    def binop(self, node):
        self._print(" " + node.sym + " ")

    def visit_lt(self, node):
        self.binop(node)

    def visit_gt(self, node):
        self.binop(node)

    def visit_gte(self, node):
        self.binop(node)

    def visit_lte(self, node):
        self.binop(node)

    def visit_neq(self, node):
        self.binop(node)

    def visit_mul(self, node):
        self.binop(node)

    def visit_eq(self, node):
        self.binop(node)

    def visit_modulus(self, node):
        self.binop(node)

    def visit_sub(self, node):
        self.binop(node)
