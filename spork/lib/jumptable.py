
"""

Jump table construct 

used to run code base on enumeration 

get jump ref as an integer

guard the integer size
- table 
ref1
ref2
ref3

ref1:
 code
 code 
 code
 J(end)

ref2:
 code
 code 
 code
 J(end)

end:

"""

from ..firmware.base import *
from ..logger import logger


from boneless.arch.opcode import Instr
from boneless.arch.opcode import *

from enum import IntEnum, auto

log = logger(__name__)


class TestEnum(IntEnum):
    one = auto()
    two = auto()
    three = auto()


class JumpTable:
    def __init__(self, enumer):
        self.commands = {}
        self.items = []
        if type(enumer) is not type(IntEnum):
            raise ("Not an enumeration")
        for i in enumer:
            log.critical(i)
            self.items.append(i)

    def __call__(self, reg):
        log.critical("Return code")
        return []


if __name__ == "__main__":
    log.critical("JUMP TABLE")
    jt = JumpTable(TestEnum)
    print(jt)
    c = jt(0)
    print(c)
