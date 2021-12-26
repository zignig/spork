#!/usr/bin/python3
"""
Parser start
"""
from lark import Lark, Transformer, v_args, Visitor
import sys
from compiler.program import Program
from compiler.base import Base


gram = r"""
    start: ( _ent )*
    _ent: ( task | func | impl |  enum | proc | on | statement | comment | struct | return | use | _NL ) 
    enum: "enum" ident eitems 
    eitems: "{" [ ident ("," ident )*] "}"
    struct: "struct" ident _fields
    task: "task" ident body  -> task
    func: "func" ident declparam body -> func
    impl: "impl" ident declparam body -> impl 
    proc: "proc" ident param body -> proc
    on: "on" ident body -> on_event
    return: "return" expr -> returner 
    use: "use" ident -> use
    
    declparam: "(" [ dvar ("," dvar )*] ")"
    dvar:  TYPE [ array ] ident [ set_var ] 

    _fields: "{" ( var | _NL)*  "}"
    comment: /\/\/[^\n]*/ 
    ident: NAME ("." ident)*
    index: ident "[" expr "]"
    param: "(" [ _item ("," _item )*] ")"
    body: "{" _ent* "}" 
    _item: expr 

    ?statement: ( var | assign | call | if | while | body ) _NL
    assign: ( ident | index ) "=" expr 
    call: ident param
    var: "var" TYPE [ array ] ident [ set_var ] -> variable
    array: "[" [NUMBER] "]"
    set_var: "=" expr 

    // expressions 
    ?expr: product
        | expr "+" product   -> add
        | expr "-" product   -> sub

    ?product: atom
        | product "*" atom  -> mul
        | product "/" atom  -> div

    ?atom: NUMBER           -> number
         | "-" atom         -> neg
         | ident            -> var 
         | "(" expr ")"
         | call
         | ESCAPED_STRING

    
    if: "if" eval body [ else ] -> iffer
    else: "else" body -> elser
    
    while: "while" eval body -> whiler
    
    eval: "(" (NUMBER | compare | expr | call | ident) ")" -> evaler

    // comparisions 
    compare: expr _comp expr
    _comp: (gt | lt | lte | gte | eq | neq)
    gt: ">"
    lt: "<"
    lte: "<="
    gte: ">="
    eq: "=="
    neq: "!="

    TYPE: NAME
    %import common.NUMBER
    %import common.CNAME -> NAME
    %import common.WS_INLINE
    %import common.ESCAPED_STRING
    %ignore WS_INLINE

    _NL: /(\r?\n[\t ]*)+/
"""


@v_args(inline=True)
class BoneTree(Transformer):
    """
        This is the main trasnform tree, it takes the parse tree
        and converts it into a collection of python objects as an ast.
    """

    from compiler.eval import add, var, variable, mul, div, sub, assign, evaler
    from compiler.ident import param, ident, declparam
    from compiler.call import call, comment, fields, dvar
    from compiler.structure import func, task, proc, impl, on_event, use, returner
    from compiler.control import iffer, whiler
    from compiler.data import number, array, struct, enum, index
    from compiler.program import Program
    from compiler.compare import compare, lt, gt, lte, gte, eq, neq

    def start(self, *data):
        return Program(data)

    def body(self, *body):
        return body


class Vi(Visitor):
    pass


bt = BoneTree()
main_parser = Lark(gram, parser="lalr", propagate_positions=True)
p = main_parser.parse
data = None
v = Vi()


class Compiler:
    def __init__(self, data):
        self.data = data


from compiler.display import Display 
from compiler.gensymbols import GenSymbols

from pprint import pprint

if __name__ == "__main__":
    if len(sys.argv) > 1:
        f = sys.argv[1]
        d = open(f).read()
    else:
        print("default file fib.prg")
        d = open("small.prg").read()
    #print(" ----- original -----")
    #print(d)
    #print(" ----- parsed -----")
    data = p(d)
    #print(data.pretty())
    trans = bt.transform(data)
    d = Display()
    print(" ----- AST -----")
    d.visit(trans)
    print("--------- Scan Symbols -----------")
    gs = GenSymbols()
    gs.visit(trans)
    print("----- Symbols ----")
    print(trans.symbols)
    
