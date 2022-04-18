from nmigen import *

from ..cores.periph import Peripheral
from ..utils.search import Enroll

__all__ = ["LedPeripheral"]


@Enroll(driver=["led", "user_led"])
class LedPeripheral(Peripheral, Elaboratable):
    """Led peripheral.

    CSR registers
    -------------
    val : read/write
        Set the value of the Leds
    en : read/write
        enable leds.
    """

    def __init__(self, leds):
        super().__init__()

        self.leds = leds

        bank = self.csr_bank()
        self.led = bank.csr(16, "rw")
        self._en = bank.csr(1, "rw")

    def elaborate(self, platform):
        m = Module()
        m.submodules.bridge = self._bridge

        with m.If(self._en.w_data):
            m.d.comb += self.leds.eq(self.led.w_data)
        with m.Else():
            m.d.comb += self.leds.eq(0)
        return m
