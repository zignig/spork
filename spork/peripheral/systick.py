from nmigen import *

from ..cores.periph.base import Peripheral
from ..utils.search import Enroll

from ..logger import logger

log = logger(__name__)

__all__ = ["TimerPeripheral"]


@Enroll(provides="systick")
class SysTick(Peripheral, Elaboratable):
    """systick peripheral.

    A general purpose counter, for system time.

    Uses the default clock to make a realtime increment
    """

    def __init__(self, interval):
        super().__init__(name=name)

        self.width = width

        bank = self.csr_bank()
        self.counter = bank.csr(16, "rw")
        self._zero_ev = self.event(mode="rise")

    def elaborate(self, platform):
        m = Module()
        # Remeber to attach the bridge
        m.submodules.bridge = self._bridge

        return m
