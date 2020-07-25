# stored string handling functions

from ideal_spork.firmware.base import *
from ideal_spork.logger import logger


from boneless.arch.opcode import Instr
from boneless.arch.opcode import *

log = logger(__name__)

import random

# TODO , strings are currently word encoded , wastes a lot of space
# have a compact version that byte packs them, use top bit as switch
# limits string length to 15 bits


class SingleString:
    """ A single string with prefix and 
        If it has been called , _used is true and it is added to the string data in the firmware
    """

    def __init__(self, name, value, postfix):
        self.name = name
        self.value = value
        self._postfix = postfix

        self._used = False

    def get_name(self):
        return self.name + self._postfix

    def __call__(self, register):
        self._used = True
        return [MOVR(register, self.get_name())]

    def as_mem(self):
        length = len(self.value)
        chars = [ord(c) for c in self.value]
        return [L(self.name + self._postfix), Rem(self.value), length, chars]


class Stringer(CodeObject):
    " Collection of string objects "

    def __init__(self, postfix=None):
        super().__init__()
        # need to make attrs like this becuase of the __setattr__
        object.__setattr__(self, "_strings", {})

    @property
    def _used(self):
        used = False
        for i in self._strings:
            single = self._strings[i]
            if single._used:
                used = True
                break
        return used

    def __setattr__(self, item, value):
        val = SingleString(item, value, self._postfix)
        self._strings[item] = val
        object.__setattr__(self, item, val)

    def code(self):
        string_rep = [Rem("String Construct")]
        for i in self._strings:
            single = self._strings[i]
            if single._used:
                string_rep += single.as_mem()

        return string_rep

    def show(self):
        print(self.code())


if __name__ == "__main__":
    s = Stringer()
    s.one = "this is a test"
    s.two = "this is another test"
    # s.one(R0)
    s.boot_string = "Boneless Bootloader"
