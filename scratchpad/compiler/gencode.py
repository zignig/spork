# Walk the tree and generate three value tuples

from .visitor import NodeVisitor
from .resolver import Resolver, Labels
from .instrselect import InstructionSelector
from .section import *
from .allocator import *
import pprint


class GenCode(NodeVisitor):
    def __init__(self, display=False):
        self._display = display
        self._code = []
        self.resolver = Resolver()
        self.labels = Labels()
        self.selector = InstructionSelector()
        # defer generation of functions till the end
        self.deferring = True
        self.deferred = []

    def _add(self, value):
        # add an instruction the list
        self._code.append(value)

    def tripple(self, op, target, lhs, rhs):
        pass

    def show(self):
        print("THE PROGRAM")
        pprint.pprint(self._code, width=1, indent=2)

    def visit_Program(self, node):
        returnlist = [program_prelude()]
        print(node.body)
        for i in node.body:
            returnlist.append(self.visit(i))
        self.deferring = False
        for i in self.deferred:
            returnlist.append(self.visit(i))
        returnlist.append(program_epilog())
        self._code = returnlist
        pprint.pprint(returnlist)
        return returnlist

    def visit_func(self, node):
        if self.deferring:
            print("DEFER" + node.name.name)
            self.deferred.append(node)
            return
        l = self.labels
        node.label = l.set(node.name.name)
        instr = [l.set(node.name.name), function_prelude(), self.visit(node.params)]
        for i in node.body:
            instr.append(self.visit(i))
        instr.append(function_epilog())
        return [instr]

    def visit_iffer(self, node):
        l = Labels()
        node.expr.target = l.run
        instr = [
            Rem("Start if"),
            self.visit(node.expr),
            Rem(J(l.after)),
            self._add(l.run),
        ]
        instr.append(Rem("If body"))
        for i in node.body:
            instr.append(self.visit(i))
        instr.append([l.after, Rem("end if")])
        return instr

    def visit_whiler(self, node):
        l = Labels()
        instr = [Rem("while start"), J(l.expr), L(l.again)]
        for i in node.body:
            instr.append(self.visit(i))
        instr.append(L(l.expr))
        # target the branch
        node.expr.target = l.again
        instr.append(self.visit(node.expr))
        return instr

    def visit_returner(self, node):
        return self.visit(node.expr)

    def binop(self, node):
        " binary operation "
        lhs = self.visit(node.lhs)
        rhs = self.visit(node.rhs)
        tmp = self.resolver.new()
        self._add(node.instr + "(" + str(tmp) + "," + str(lhs) + "," + str(rhs) + ")")
        return tmp

    def visit_number(self, node):
        new_reg = self.resolver.new(node.name)
        node.reg = new_reg
        self._add("MOVI(" + str(new_reg) + "," + node.val + ")")
        return new_reg

    def visit_evaluate(self, node):
        # push the target down
        node.comp.target = node.target
        return self.visit(node.comp)

    def visit_compare(self, node):
        rhs = self.visit(node.rhs)
        lhs = self.visit(node.lhs)
        instr = []
        instr.append(CMP(lhs, rhs))
        # push the target down
        node.op.target = node.target
        instr.append(self.visit(node.op))
        return instr

    def visit_assign(self, node):
        rhs = self.visit(node.rhs)
        lhs = self.visit(node.lhs)
        instr = []
        instr.append(Rem("assign"))
        instr.append(str(node))
        self._add("MOV(" + str(lhs) + "," + str(rhs) + ")")
        return instr

    def visit_ident(self, node):
        return self.resolver.name(node.name)

    def visit_call(self, node):
        target = node.local_symbols.get(node.name)
        instr = []
        for i in node.params:
            instr.append(self.visit(i))
        instr.append(Rem("call" + node.name))
        # self._add("JSR(R7,"+target.label+")")
        instr.append(Rem("return" + node.name))
        return instr

    def visit_stringer(self, node):
        new_reg = self.resolver.new()
        self._add("resolve " + str(node))
        return new_reg

    def visit_param(self, node):
        instr = []
        for i in node.params:
            instr.append(self.visit(i))
        return instr

    def visit_var(self, node):
        new_reg = self.resolver.name(node.name.name)
        self._add("resolve " + node.name.name + " -> " + str(new_reg))
        return new_reg

    def condbr(self, node):
        instr = self.selector.select(type(node))
        return instr(node.target)

    def visit_variable(self, node):
        if node.setvar is not None:
            self.visit(node.setvar)

    def visit_setvar(self, node):
        self.visit(node.expr)

    def visit_div(self, node):
        return self.binop(node)

    def visit_lt(self, node):
        return self.condbr(node)

    def visit_gt(self, node):
        return self.condbr(node)

    def visit_gte(self, node):
        return self.condbr(node)

    def visit_lte(self, node):
        return self.condbr(node)

    def visit_neq(self, node):
        return self.condbr(node)

    def visit_mul(self, node):
        return self.condbr(node)

    def visit_eq(self, node):
        return self.condbr(node)

    def visit_modulus(self, node):
        return self.binop(node)

    def visit_sub(self, node):
        return self.binop(node)

    def visit_add(self, node):
        return self.binop(node)

    def visit_comment(self, node):
        pass

    def visit_declparam(self, node):
        pass

    def visit_const(self, node):
        pass
