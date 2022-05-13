"""
    System tick generator.

    Raises a flag when it is needed and has a scaling factor.

    1000Hz seems to be a standard interval for events.
"""

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

    def __init__(self, inter=0x0F00, mul=1):
        log.info("Create Systick Peripheral")
        super().__init__()

        self.inter = inter
        self.mul = mul
        bank = self.csr_bank()
        self.interval = bank.csr(16, "rw")
        self.multiplier = bank.csr(16, "rw")
        self.counter = Signal(16)
        self.mul_counter = Signal(16)
        self.active = self.event(mode="rise")

        self.startup = Signal()

    def elaborate(self, platform):
        m = Module()
        # Remember to attach the bridge
        m.submodules.bridge = self._bridge
        # the systick counter
        with m.If(self.startup == 0):
            m.d.sync += self.interval.r_data.eq(self.inter)
            m.d.sync += self.multiplier.r_data.eq(self.mul)
            m.d.sync += self.startup.eq(1)
        with m.Else():
            # update the counter
            with m.If(self.counter == self.interval.r_data):
                m.d.sync += self.counter.eq(0)
                m.d.comb += self.active.stb.eq(1)
            with m.Else():
                with m.If(self.mul_counter == self.multiplier.r_data):
                    m.d.sync += self.mul_counter.eq(0)
                    m.d.sync += self.counter.eq(self.counter + 1)
                with m.Else():
                    m.d.sync += self.mul_counter.eq(self.mul_counter + 1)

        # update the registers with a write
        with m.If(self.multiplier.w_stb):
            m.d.sync += self.multiplier.r_data.eq(self.multiplier.w_data)
        with m.If(self.interval.w_stb):
            m.d.sync += self.interval.r_data.eq(self.interval.w_data)
        return m
