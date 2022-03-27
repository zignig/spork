#!/usr/bin/python
" Boneless instruction Exposition"

from boneless.arch.opcode import Instr
from boneless.arch.opcode import *
from rich import print

instructions = ADD.mnemonics


for i in instructions:
    item = instructions[i]
    # for j in item.__mro__[0:-3]:
    #    print("{:<7} {}".format(j.__name__,j.coding))
    print("{} {:<7} {}".format(int(item.coding[0:4], 2), i, item.coding))
