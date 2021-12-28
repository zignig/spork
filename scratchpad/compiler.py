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

from pprint import pprint
_DEBUG = False 
#_DEBUG = True 

if __name__ == "__main__":
    if len(sys.argv) > 1:
        f = sys.argv[1]
        program_file  = open(f).read()
    else:
        print("default file small.prg")
        program_file = open("small.prg").read()
    print("---- preprocess ----")
    pp = Preprocessor(program_file)
    pp.start()
    
    print(pp)
    print("---- parse ----")
    pa = Parser()
    for i in pp.data_dict:
        print('build '+i)
        d = pa.parse(pp.data_dict[i])
        print(d.pretty())
    data = pa.parse(program_file)
    print(" ----- parsed -----")
    if _DEBUG:
        print(data.pretty())
    bt = BoneTree()
    trans = bt.transform(data)
    d = Display()
    print(" ----- AST -----")
    d.visit(trans)
    d.show()
    if _DEBUG: 
        print("--------- Scan Symbols -----------")
        gs = GenSymbols(display=True)
        gs.visit(trans)
        print("----- Symbols ----")
        print(trans.symbols)
        print("---- Syntax Checker ----")
        sc = SyntaxCheck()
        sc.visit(trans) 
