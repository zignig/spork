# Display the AST 
# Just a simple walker


from .visitor import NodeVisitor

class Display(NodeVisitor):

    def visit_Program(self,node):
        print("Program")
        for i in node.body:
            self.visit(i)

    def visit_func(self,node):
        print("Function")
        print(node.name)
        self.visit(node.params)
        for i in node.body:
            self.visit(i)

    def visit_declparam(self,node):
        for i in node.params:
            self.visit(i)

    def visit_assign(self,node):
        self.visit(node.lhs)
        self.visit(node.rhs)

    def visit_ident(self,node):
        print(node.name)

    def visit_add(self,node):
        print('add')
        self.visit(node.lhs)
        self.visit(node.rhs)

    def visit_var(self,node):
        print(node.name)

    def visit_number(self,node):
        print(node.val)

    def visit_comment(self,node):
        pass

    def visit_variable(self,node):
        print(node.name)

    def visit_call(self,node):
        print("Call "+node.name)
