# Node visitor
# super  class to walk the ast

class NodeVisitor(object):
    def visit(self, node):
        method_name = "visit_" + type(node).__name__
        visitor = getattr(self,method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self,node):
        print("No visit_{} method".format(type(node).__name__))
        print(node,'-> [',end=" ")
        l = dir(node)
        for i in l:
            if not i.startswith("__"):
                print(i,end=" ")
        print(']')
        #raise Exception("Node visit_{} method".format(type(node).__name__))


