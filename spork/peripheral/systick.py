from nmigen import *

from ..cores.periph.base import Peripheral
from ..utils.search import Enroll

from ..logger import logger

log = logger(__name__)

__all__ = ["SysTick"]


@Enroll(provides="systick")
class SysTick(Peripheral, Elaboratable):
    """systick peripheral.

    A general purpose ticker , for system time.

    Uses the default clock to make a realtime increment
    """

    def __init__(self, interval):
        super().__init__()

        self.interval = interval

        bank = self.csr_bank()
        self.value = bank.csr(16, "rw")
        self.divider = Signal(16, reset=interval)
        self.counter = Signal(16)

    def elaborate(self, platform):
        m = Module()
        # Remember to attach the bridge
        m.submodules.bridge = self._bridge
        # the systick counter

        # update the counter
        with m.If(self.counter == self.divider):
            m.d.sync += self.counter.eq(0)
            m.d.sync += self.value.r_data.eq(self.value + 1)
        with m.Else():
            m.d.sync += self.counter.eq(self.counter + 1)

        return m
