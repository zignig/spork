# Walk the tree and generate three value tuples  

from .visitor import NodeVisitor
from .resolver import Resolver,Labels
from .section import * 

class GenCode(NodeVisitor):
    def __init__(self):
        self._code = []
        self.resolver = Resolver()
        self.labels = Labels()

    def _add(self,value):
        # add an instruction the list 
        self._code.append(value)
        
    def tripple(self,op,target,lhs,rhs):
        pass 

    def show(self):
        print("THE PROGRAM")
        for i,j in enumerate(self._code):
            print('{:04X}'.format(i),":",j)

    def visit_Program(self,node):
        self._add("PROGRAM PRELUDE")
        for i in node.body:
            self.visit(i)
        self._add("PROGRAM EPILOG")

    def visit_func(self,node):
        l = self.labels 
        node.label = l.set(node.name.name)
        self._add(l.set(node.name.name))
        self._add("FUNCTION PRELUDE "+node.name.name)
        #self._add(str(node.local_symbols))
        self.visit(node.params)
        for i in node.body:
            self.visit(i)
        self._add("FUNCTION EPILOG "+node.name.name+"\n")

    def visit_iffer(self,node):
        l = Labels()
        self._add("START IF")
        self.visit(node.expr)
        self._add("jump "+l.after)
        self._add(l.run)
        for i in node.body:
            self.visit(i)
        self._add(l.after)
        self._add("END IF")

    def visit_whiler(self,node):
        l = Labels()
        self._add("WHILE START")
        self._add("J("+l.expr+")")
        self._add("L("+l.again+")")
        for i in node.body:
            self.visit(i)
        self._add("L("+l.expr+")")
        # target the branch
        node.expr.target = l.again
        self.visit(node.expr)
        self._add("WHILE END")

    def visit_returner(self,node):
        self.visit(node.expr)

    def visit_assign(self,node):
        self.visit(node.rhs)
        
    def binop(self,node):
        " binary operation "
        lhs = self.visit(node.lhs)
        rhs = self.visit(node.rhs)
        tmp = self.resolver.new()
        self._add(node.instr+'('+str(tmp)+','+str(lhs)+','+str(rhs)+')')
        return tmp

    def visit_number(self,node):
        new_reg = self.resolver.new(node.name)
        node.reg = new_reg
        self._add("MOVI("+str(new_reg)+','+node.val+')')
        return new_reg
    
    def visit_evaluate(self,node):
        return self.visit(node.comp) 
    
    def visit_compare(self,node):
        rhs = self.visit(node.rhs) 
        lhs = self.visit(node.lhs)
        self._add("CMP("+str(lhs)+','+str(rhs)+")")
        self.visit(node.op)
 
    def visit_assign(self,node):
        rhs = self.visit(node.rhs)
        lhs = self.visit(node.lhs)
        self._add('MOV('+str(lhs)+','+str(rhs)+')')
        
    def visit_ident(self,node):
        return self.resolver.new(node.name)

    def visit_call(self,node):
        target = node.local_symbols.get(node.name)
        self._add("call "+node.name)
        self.visit(node.params)
        self._add("JSR(R7,"+target.label+")")
        self._add("copy return")
        

    def visit_param(self,node):
        for i in node.params:
            self._add(i)
            self.visit(i)

    def visit_var(self,node):
        new_reg = self.resolver.new(node.name.name)
        self._add("resolve "+node.name.name+' -> '+str(new_reg))
        return new_reg

    def condbr(self,node):
        self._add(node.instr)
        return node.instr

    def visit_variable(self,node):
        if node.setvar is not None:
            print("SET VAR")

    def visit_add(self,node): return self.binop(node)
    def visit_sub(self,node): return self.binop(node)
    def visit_div(self,node): return self.binop(node)
    def visit_mul(self,node): return self.binop(node)
    def visit_modulus(self,node): return self.binop(node)
        
    def visit_lt(self,node): return self.condbr(node)
    def visit_eq(self,node): return self.condbr(node)
    def visit_gt(self,node): return self.condbr(node)
        
    def visit_comment(self,node):pass
    def visit_declparam(self,node):pass
    def visit_const(self,node):pass

