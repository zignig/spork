#!/usr/bin/python3
"""
Parser start
"""
from lark import Lark, Transformer, v_args, Visitor
import sys
from abstr import program

gram = r"""
    start: ( _ent )*
    _ent: ( task | func | enum | proc | on | statement | comment | struct | return | use | _NL ) 
    enum: "enum" ident eitems 
    eitems: "{" [ ident ("," ident )*] "}"
    struct: "struct" ident _fields
    task: "task" ident body  -> task
    func: "func" ident param body -> func
    proc: "proc" ident param body -> proc
    on: "on" ident body -> on_event
    return: "return" expr -> returner 
    use: "use" ident -> use
    
    _fields: "{" (var | _NL)*  "}"
    comment: /\/\/[^\n]*/ 
    ident: NAME ("." ident)*
    param: "(" [ _item ("," _item )*] ")"
    body: "{" _ent* "}" 
    _item: expr 

    ?statement: ( var | assign | call | if | while | body ) _NL
    assign: ident "=" expr 
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
    
    eval: "(" (expr _comp expr | call | ident) ")"

    // comparisions 
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
    # arith
    from abstr import add, var, variable, mul, div, sub
    from abstr import param, number, ident
    from abstr import call, struct, comment, fields
    from abstr import func, task, program, assign, proc
    from abstr import iffer, whiler, on_event
    from abstr import array, returner, use
    from abstr import enum

    def start(self, *data):
        return program(data)

    def body(self, *body):
        return body


class Vi(Visitor):
    pass


bt = BoneTree()
main_parser = Lark(gram, parser="lalr")
p = main_parser.parse
data = None
v = Vi()


class Compiler:
    def __init__(self):
        pass


if __name__ == "__main__":
    if len(sys.argv) > 1:
        f = sys.argv[1]
        d = open(f).read()
    else:
        print("default file base.prg")
        d = open("base.prg").read()
    data = p(d)
    print(data.pretty())
    trans = bt.transform(data)
    print("------ transformed -------")
    print()
    print(trans)
    instr = trans.start_walk()
    print("---------symbols-----------")
    print(trans.symbols)
    print("---------instructions-----------")
    print(instr)
