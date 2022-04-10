from boneless.arch.opcode import Instr
from boneless.arch.opcode import *

from ..firmware.base import *

from .stringer import Stringer

from ..logger import logger

log = logger(__name__)


class Switch:
    " Construct a jump table for single chars, or integers "

    def __init__(self, window, select, default=None):
        self.mapping = {}
        self.labels = LocalLabels()
        self.window = window
        self.select = select  # a register in window

    def add(self, item):
        if len(item) != 2:
            raise FWError()
        if isinstance(item, list):
            for i in item:
                self.add(i, item)
        val = item[0]
        subroutine = item[1]
        # insert the mapping
        if isinstance(val, str):
            val = ord(val)
            self.mapping[val] = subroutine
        elif isinstance(val, int):
            self.mapping[val] = subroutine

    def __call__(self):
        ll = self.labels
        w = self.window
        data = [Rem("start of the jump table")]
        # map the values
        for i, j in enumerate(self.mapping):
            # log.debug("{:d} -> {:d} -> {:s}".format(i, j, str(self.mapping[j])))
            data += [
                [
                    Rem("start-" + str(j)),
                    CMPI(self.select, j),
                    BZ("{:04d}{:s}".format(i, ll._postfix)),
                    Rem("end-" + str(j)),
                ]
            ]
        data += [J(ll.table_end), Rem("end of jump table")]
        for i, j in enumerate(self.mapping):
            # log.debug("trace {:d} -> {:d} -> {:s}".format(i, j, str(self.mapping[j])))
            data += [[ll("{:04d}".format(i)), self.mapping[j], J(ll.table_end)]]
        data += [ll("table_end")]
        return data
