# stored string handling functions

from ideal_spork.firmware.base import *
from ideal_spork.logger import logger


from boneless.arch.opcode import Instr
from boneless.arch.opcode import *

log = logger(__name__)


class SingleString:
    def __init__(self, name, value):
        self.name = name
        self.value = value
        self._used = False

    def __call__(self):
        self._used = True
        return self.value

    def as_mem(self):
        length = len(self.value)
        chars = [ord(c) for c in self.value]
        return [L(self.name), length, chars]


class Stringer(CodeObject):
    " Collection of string objects "

    def __init__(self):
        super().__init__()
        object.__setattr__(self, "_strings", {})
        log.critical("Unfinished")

    def __setattr__(self, item, value):
        self._strings[item] = SingleString(item, value)

    def __getattr__(self, item):
        return self._strings[item]

    def show(self):
        for i in self._strings:
            single = self._strings[i]
            if single._used:
                print(single.as_mem())

    def code(self):
        return [Rem("String code object goes here"), [0]]


if __name__ == "__main__":
    s = Stringer()
    s.one = "this is a test"
    s.two = "this is another test"
    s.show()
    s.one()
    s.two()
    s.boot_string = "Boneless Bootloader"
    s.boot_string()
    s.show()
