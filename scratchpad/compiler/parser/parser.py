from lark import Lark, Transformer, v_args, Visitor
import sys
from ..ast.program import Program
from ..ast.base import Base


gram = r"""
    start: ( _ent )*
    _ent: ( task | func | impl |  enum | proc | on | statement | comment | struct | return | use | _NL ) 

    enum: "enum" ident eitems 
    eitems: "{" [ ident ("," ident )*] "}"
    struct: "struct" ident _fields

    task: "task" ident body  -> task
    func: "func" ident declparam body -> func
    impl: "impl" ident declparam body -> impl 
    proc: "proc" ident _param body -> proc
    on: "on" ident body -> on_event
    return: "return" expr -> returner 
    use: "use" [ ident ("," ident)* ] _NL  -> use
    
    declparam: "(" [ dvar ("," dvar )*] ")"
    dvar:  TYPE ident [ array ] [ set_var ] 

    _fields: "{" ( var | func | enum | _NL)*  "}"
    comment: /\/\/[^\n]*/ 

    // dotted notation
    ident: NAME ["." dotted] -> ident
    dotted: NAME ["." dotted] -> dotted

    index: ident "[" expr "]"
    _param: "(" [ _item ("," _item )*] ")"
    body: "{" _ent* "}" 
    _item: expr 

    ?statement: ( var | const | assign | call | if | while | body ) _NL
    assign: ( ident | index ) "=" expr 
    call: ident _param
    const: "const" TYPE[ array ] ident  [ set_var ] -> const
    var: "var" ( array | TYPE ) ident  [ set_var ] -> variable
    array: TYPE "[" [expr] "]"
    set_var: "=" expr  -> setvar

    // expressions 
    ?expr: product
        | expr "+" product   -> add
        | expr "-" product   -> sub

    ?product: atom
        | product "*" atom  -> mul
        | product "/" atom  -> div
        | product "**" atom  -> pow 
        | product "%" atom  -> modulus 
        | product "<<" atom  -> shl
        | product ">>" atom  -> shr

    ?atom: NUMBER           -> number
         | "-" atom         -> neg
         | ident            -> var 
         | index            -> index
         | "(" expr ")"
         | call
         | ESCAPED_STRING   -> stringer

    
    if: "if" evaluate body [ else ] -> iffer
    else: "else" body -> elser
    
    while: "while" evaluate body -> whiler
    
    evaluate: "(" ( compare | call | truthy ) ")" -> evaluate
    truthy: ident -> truthy // must be boolean
    // comparisions 
    compare: expr _comp expr -> compare
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


@v_args(inline=True, meta=True)
class BoneTree(Transformer):
    """
    This is the main transform tree, it takes the parse tree
    and converts it into a collection of python objects as an ast.
    """

    from ..ast.eval import (
        add,
        var,
        variable,
        mul,
        div,
        sub,
        assign,
        const,
        setvar,
        stringer,
        modulus,
    )
    from ..ast.ident import param, ident, declparam, dotted
    from ..ast.call import call, comment, fields, dvar
    from ..ast.structure import (
        func,
        task,
        proc,
        impl,
        on_event,
        use,
        returner,
        evaluate,
    )
    from ..ast.control import iffer, whiler
    from ..ast.data import number, array, struct, enum, index
    from ..ast.program import Program
    from ..ast.comp import lt, gt, lte, gte, eq, neq, compare

    def start(self, meta, *data):
        return Program(data)

    def body(self, meta, *body):
        return body


class Parser:
    def __init__(self):
        self._parser = Lark(gram, parser="lalr", propagate_positions=True)

    def parse(self, program_data):
        p = self._parser.parse
        tree = p(program_data)
        return tree
