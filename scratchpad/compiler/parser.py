from lark import Lark, Transformer, v_args, Visitor
import sys
from .program import Program
from .base import Base


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
    use: "use" [ ident ("," ident)* ] _NL  -> use
    
    declparam: "(" [ dvar ("," dvar )*] ")"
    dvar:  TYPE [ array ] ident [ set_var ] 

    _fields: "{" ( var | func | enum | _NL)*  "}"
    comment: /\/\/[^\n]*/ 
    ident: NAME ("." ident)*
    index: ident "[" expr "]"
    param: "(" [ _item ("," _item )*] ")"
    body: "{" _ent* "}" 
    _item: expr 

    ?statement: ( var | const | assign | call | if | while | body ) _NL
    assign: ( ident | index ) "=" expr 
    call: ident param
    const: "const" TYPE [ array ] ident [ set_var ] -> const
    var: "var" TYPE [ array ] ident [ set_var ] -> variable
    array: "[" [NUMBER|ident] "]"
    set_var: "=" expr 

    // expressions 
    ?expr: product
        | expr "+" product   -> add
        | expr "-" product   -> sub

    ?product: atom
        | product "*" atom  -> mul
        | product "/" atom  -> div
        | product "**" atom  -> pow 
        | product "%" atom  -> modulus 

    ?atom: NUMBER           -> number
         | "-" atom         -> neg
         | ident            -> var 
         | index
         | "(" expr ")"
         | call
         | ESCAPED_STRING   -> str

    
    if: "if" evaluate body [ else ] -> iffer
    else: "else" body -> elser
    
    while: "while" evaluate body -> whiler
    
    evaluate: "(" ( expr | call | ident | _compare ) ")" -> evaluate

    // comparisions 
    _compare: expr _comp expr 
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

    from .eval import add, var, variable, mul, div, sub, assign, const
    from .ident import param, ident, declparam
    from .call import call, comment, fields, dvar
    from .structure import func, task, proc, impl, on_event, use, returner, evaluate
    from .control import iffer, whiler
    from .data import number, array, struct, enum, index
    from .program import Program
    from .comp import lt, gt, lte, gte, eq, neq,compare

    def start(self, *data):
        return Program(data)

    def body(self, *body):
        return body

class Parser:
    def __init__(self):
        self._parser = Lark(gram, parser="lalr", propagate_positions=True)

    def parse(self,program_data):
        p = self._parser.parse
        tree = p(program_data)
        return tree
