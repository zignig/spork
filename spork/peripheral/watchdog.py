from nmigen import *

from ..cores.periph import Peripheral
from ..utils.search import Enroll
from ..logger import logger

log = logger(__name__)


@Enroll(platform="ice40", provides="watchdog")
class Watchdog(Peripheral, Elaboratable):
    def __init__(self, cpu, bits=24):
        log.info("Create Watchdog Peripheral")
        super().__init__()
        bank = self.csr_bank()

        self.bits = bits
        self.reset_val = 2**bits - 1

        self._en = bank.csr(1, "rw")
        self._poke = bank.csr(1, "w")
        self._interval = bank.csr(16, "rw")

        self.enable = Signal()
        self.counter = Signal(self.bits, reset=self.reset_val)
        self.reset = Signal()

    def elaborate(self, platform):
        m = Module()
        m.submodules.bridge = self._bridge

        with m.If(self._en.w_stb):
            m.d.sync += self.enable.eq(self._en.w_data)

        with m.If(self.enable):
            with m.If(self._poke.w_stb):
                m.d.sync += self.counter.eq(self.reset_val)
            with m.Else():
                m.d.sync += self.counter.eq(self.counter - 1)

        with m.If(self.counter == 0):
            m.d.sync += self.reset.eq(1)

        return m
