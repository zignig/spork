#!/usr/bin/python3.6
"""
Compiler front end 
"""
import sys

from compiler.display import Display 
from compiler.gensymbols import GenSymbols
from compiler.preprocess import Preprocessor
from compiler.parser import Parser,BoneTree
from compiler.syntaxcheck import SyntaxCheck 
from compiler.gencode import GenCode

from pprint import pprint
_DEBUG = True 
#_DEBUG = False 

# transfer this contruct down into class once it 
# is listening to instructions 

class Build:
    " make some code"
    def __init__(self,code):
        self.code = code
        self.parse_tree = None
        self.ast = None
        self.assembly = []

    def header(self,value):
        print('---- '+value+' ----')

    def run(self):
        self.header('parser')
        pa = Parser()
        self.parse_tree = pa.parse(self.code)
        self.header('ast')
        bt = BoneTree()
        self.ast = bt.transform(self.parse_tree)
        self.header('display')
        d = Display()
        d.visit(self.ast)
        #d.show()
        self.header('generate symbols')
        gs = GenSymbols()
        gs.visit(self.ast)

        self.header('syntax check')
        sc = SyntaxCheck()
        sc.visit(self.ast)

        self.header('generate code')
        gc = GenCode(display=True)
        gc.visit(self.ast)
        gc.show()
        
        
import yaml         

if __name__ == "__main__":
    if len(sys.argv) > 1:
        f = sys.argv[1]
        program_file  = open(f).read()
    else:
        print("default file small.prg")
        program_file = open("small.prg").read()
    print("---- original ----")
    #print(program_file)
    print("---- preprocess ----")
    pp = Preprocessor(program_file)
    pp.start()
    if _DEBUG: 
        print(pp)
    pa = Parser()
    for i in pp.data_dict:
        print('build '+i)
        d = pa.parse(pp.data_dict[i])
        print(d.pretty())
    builder =Build(program_file)
    builder.run()
    yaml.dump(builder.ast)
    
"""
    data = pa.parse(program_file)
    print("----- parsed -----")
    if _DEBUG:
        print(data.pretty())
    bt = BoneTree()
    trans = bt.transform(data)
    if _DEBUG:
        d = Display()
        d.visit(trans)
        d.show()
    print("----- AST -----")
    if _DEBUG: 
        print("--------- Scan Symbols -----------")
        gs = GenSymbols()
        gs.visit(trans)
        print("----- Symbols ----")
        print(trans.symbols)
        print("---- Syntax Checker ----")
        sc = SyntaxCheck(display=True)
        sc.visit(trans) 
        print("---- Generate Code ----")
    gc = GenCode()
    gc.visit(trans)
    gc.show()
"""
