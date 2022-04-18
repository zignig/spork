"Use the ice40 warmboot from code"

from boneless.arch.opcode import Instr
from boneless.arch.opcode import *

from ..firmware.base import *


class WarmBoot(SubR):
    "Warmboot the device"

    def setup(self):
        self.params = ["image"]
        self.locals = ["temp"]

    def instr(self):
        w = self.w
        reg = self.reg
        ll = LocalLabels()
        return [
            STXA(w.image, reg.warm.image),
            MOVI(w.temp, 1),
            STXA(w.temp, reg.warm.en),
        ]
