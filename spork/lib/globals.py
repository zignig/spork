" make space for a global stored registers "

from ..firmware.base import *
from ..logger import logger


from boneless.arch.opcode import Instr
from boneless.arch.opcode import *

log = logger(__name__)


class _glob_var:
    """ 
        make a labeled construct of 
        If it has been called , _used is true and it is added to the string data in the firmware
    """

    def __init__(self, name, value, postfix, compact=True):
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
        return [L(self.name + self._postfix), Rem(self.value), self.value]


class Globals(CodeObject):
    " Collection of global single register variables, all labeled"

    def __init__(self, postfix=None, compact=True):
        super().__init__()
        # need to make attrs like this because of the __setattr__
        object.__setattr__(self, "_globals", {})

    @property
    def _used(self):
        used = False
        for i in self._globals:
            single = self._globals[i]
            if single._used:
                used = True
                break
        return used

    def __setattr__(self, item, value):
        val = _glob_var(item, value, self._postfix)
        self._globals[item] = val
        object.__setattr__(self, item, val)

    def code(self):
        string_rep = [Rem("Globals")]
        for i in self._globals:
            single = self._globals[i]
            if single._used:
                string_rep += single.as_mem()

        return string_rep

    def show(self):
        print(self.code())
