# instruction selector

from .allocator import *
from ..parser.vartypes import *
from ..ast.eval import add

# include compiler intrisics in this  table

# select comparison instructions
from ..ast.comp import lt, gt, lte, gte, eq, neq


class InstructionSelector:
    def __init__(self):
        self.table = {
            (add, Vint, Vint): ADD,
            (eq): BEQ,
            (gt): BGTS,
            (lt): BLTS,
            (lte): BLES,
            (gte): BGES,
            (neq): BNE,
            # TODO Include signed version
        }

    def select(self, find):
        # select instructions base on tuple
        # to double check and fail hard
        if find in self.table:
            return self.table[find]
        raise BaseException("no instruction")
