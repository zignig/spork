# Node visitor
# super  class to walk the ast

from lark.tree import Tree

class NodeVisitor(object):
    _display = False 
    def __init__(self,display=False):
        self._display = display

    def visit(self, node):
        method_name = "visit_" + type(node).__name__
        visitor = getattr(self,method_name, self.generic_visit)
        if self._display:
            print('->',method_name,' -- ',node)
        return visitor(node)

    def generic_visit(self,node):
        # Run this when defn does not exist
        print("No visit_{} method in {}".format(type(node).__name__,type(self).__name__))
        print(node,'-> [',end=" ")
        if(isinstance(node,Tree)):
            print("not parsing ",node)
        l = dir(node)
        for i in l:
            if not i.startswith("__"):
                print(i,end=" ")
        print(']\n')
        #raise Exception("Node visit_{} method".format(type(node).__name__))


