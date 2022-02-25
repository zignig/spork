# scan through the whole program and generate a call DAG
# with this graph the order of register resolution and calls
# can be calculated

from .visitor import NodeVisitor
from .base import SymbolTable
from .base import Base


class GraphNode:
    def __init__(self, node=None):
        self.children = []
        self.node = node

    def add(self, node):
        self.children.append(node)

    def show(self, depth=1):
        print(depth * "-" + str(self.node))
        if len(self.children) > 0:
            depth = depth + 1
            for j in self.children:
                j.show(depth)


class CallGraph(NodeVisitor):
    def __init__(self, display=False):
        super().__init__(display)
        self.graph = GraphNode()
        # current node
        self.current = self.graph

    def show(self):
        self.graph.show()

    def visit_Program(self, node):
        for i in node.body:
            self.visit(i)

    def visit_comment(self, node):
        pass

    def visit_func(self, node):
        new_node = GraphNode(node)
        self.current.add(new_node)
        temp = self.current
        self.current = new_node
        for i in node.body:
            self.visit(i)
        self.current = temp

    def visit_number(self, node):
        pass

    def visit_variable(self, node):
        node.detail()

    def visit_whiler(self, node):
        self.visit(node.expr)
        for i in node.body:
            self.visit(i)

    def visit_evaluate(self, node):
        self.visit(node.comp)

    def visit_compare(self, node):
        self.visit(node.lhs)
        self.visit(node.rhs)

    def visit_var(self, node):
        pass

    def visit_assign(self, node):
        self.visit(node.lhs)
        self.visit(node.rhs)

    def visit_ident(self, node):
        pass

    def binop(self, node):
        pass

    def visit_add(self, node):
        self.binop(node)

    def visit_call(self, node):
        print("DO TRICKY STUFF HERE")

    def visit_iffer(self, node):
        self.visit(node.expr)
        self.visit(node.body)
