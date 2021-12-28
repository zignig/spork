# Display the AST 
# Just a simple walker


from .visitor import NodeVisitor

class Display(NodeVisitor):
    _display = False 
    def __init__(self):
        self._data = ''
        self._indent = 0 

    def show(self):
        print(self._data) 

    def _print(self,value):
        item = '  '*self._indent + value
        self._data += item
        print(item,end='')

    def visit_Program(self,node):
        for i in node.body:
            self.visit(i)

    def visit_func(self,node):
        self._print('func '+node.name.name+'(')
        self.visit(node.params)
        self._print('){\n')
        for i in node.body:
            self._indent += 1
            self.visit(i)
            self._indent -= 1
        self._print('}\n')

    def visit_declparam(self,node):
        for i in node.params[:-1]:
            self.visit(i)
            self._print(',')
        if len(node.params) > 0:
            self.visit(node.params[-1])
    def visit_returner(self,node):
        print('return ',node)

    def visit_setvar(self,node):
        self._print(' = ')
        self.visit(node.expr)

    def visit_whiler(self,node):
        print("while")
        self.visit(node.expr)
        for i in node.body:
            self.visit(i)

    def visit_const(self,node):
        self._print('const '+node.vtype+' '+node.name.name)
        if node.setvar is not None:
            self.visit(node.setvar)
        self._print('\n') 

    def visit_assign(self,node):
        self.visit(node.lhs)
        self._print(' = ')
        self.visit(node.rhs)
        self._print('\n')

    def visit_evaluate(self,node):
        pass

    def visit_dvar(self,node):
        self._print(node.vtype + ' ' + node.name)


    def visit_ident(self,node):
        self._print(node.name)
        if node.dotted is not None: 
            self.visit(node.dotted)

    def visit_dotted(self,node):
        print("DOTTED")
        print(node.name)
        if node.dotted is not None:
            self.visit(node.dotted)

    def visit_add(self,node):
        self.visit(node.lhs)
        self._print(' + ')
        self.visit(node.rhs)

    def visit_var(self,node):
        print(node)

    def visit_number(self,node):
        self._print(node.val)

    def visit_comment(self,node):
        self._print(node.val+'\n') 

    def visit_variable(self,node):
        self._print(node.name.name)

    def visit_call(self,node):
        print(node)
        print("Call "+node.name)
