""" 
    Multiply 
    Unsigned multiply (gateware)
"""


__working__ = True
__done__ = False


from nmigen import *

from ..cores.periph.base import Peripheral
from ..utils.search import Enroll

from ..logger import logger

log = logger(__name__)

__all__ = ["Multiply"]


@Enroll(driver="multiply")
class MultiplyPeripheral(Peripheral, Elaboratable):
    """
    Gateware multiply
    """

    def __init__(self):
        log.info("Create Multiply Peripheral")
        super().__init__()
        bank = self.csr_bank()
        self.opa = bank.csr(16, "w")
        self.opb = bank.csr(16, "w")
        self.result = bank.csr(32, "r")

    def elaborate(self, platform):
        m = Module()
        m.submodules.bridge = self._bridge

        m.d.comb += self.result.r_data.eq(self.opa.w_data * self.opb.w_data)

        return m
