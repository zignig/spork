# stored string handling functions

from ..firmware.base import *
from ..logger import logger


from boneless.arch.opcode import Instr
from boneless.arch.opcode import *

log = logger(__name__)

import random

__all__ = ["SingleString", "Stringer"]

# this is nearly done , have a fence post error on newlines... 20200808
# A compact version that byte packs them, use top bit as switch
# limits string length to 15 bits, oh NO, only 32K length strings !!


class SingleString:
    """ A single string with postfix and 
        If it has been called , _used is true and it is added to the string data in the firmware
    """

    def __init__(self, name, value, postfix, compact=True):
        self.name = name
        self.value = value
        self.compact = compact
        self._postfix = postfix

        self._used = False

    def get_name(self):
        return self.name + self._postfix

    def __call__(self, register):
        self._used = True
        return [MOVR(register, self.get_name())]

    def as_mem(self):
        length = len(self.value)
        chars = []
        if self.compact:
            length = len(self.value)
            # if the length is odd , add a space
            # for the byte encoder
            if (length % 2) != 0:
                if type(self.value) == type(""):
                    self.value += " "
                else:
                    self.value += b" "

            counter = 0
            word = 0
            while counter < length:
                first_char = self.value[counter]
                second_char = self.value[counter + 1]
                if type(first_char) == type(""):
                    word = ord(first_char) << 8
                else:
                    word = first_char << 8

                if type(second_char) == type(""):
                    word = word | ord(second_char)
                else:
                    word = word | second_char

                chars.append(word)
                log.debug("val {0:016b}".format(word))
                counter += 2

            # set the high bit for compact string
            length = length | (1 << 15)
            log.debug("length {0:016b}".format(length))
        else:
            for c in self.value:
                log.debug("char -> %s", c)
                if type(c) == type(""):
                    val = ord(c)
                else:
                    val = c
                chars.append(val)
        # chop the preview string
        if len(self.value) < 20:
            comment = Rem(self.value)
        else:
            comment = Rem(self.value[:20] + " ...")
        return [L(self.name + self._postfix), comment, length, chars]


class Stringer(CodeObject):
    " Collection of string objects "

    def __init__(self, postfix=None, compact=True):
        super().__init__()
        # need to make attrs like this becuase of the __setattr__
        object.__setattr__(self, "_strings", {})
        object.__setattr__(self, "compact", compact)

    @property
    def _used(self):
        "Are any of the string used?"
        used = False
        for i in self._strings:
            single = self._strings[i]
            if single._used:
                used = True
                break
        return used

    def all(self):
        " mark all strings for use"
        for i in self._strings:
            single = self._strings[i]
            single._used = True

    def add(self, item, value):
        # Add a named label
        val = SingleString(item, value, self._postfix, self.compact)
        self._strings[item] = val
        object.__setattr__(self, item, val)

    def __setattr__(self, item, value):
        # If you assign a attr it will create a string
        val = SingleString(item, value, self._postfix, self.compact)
        self._strings[item] = val
        object.__setattr__(self, item, val)

    def code(self):
        # return all the strings a memory.
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
