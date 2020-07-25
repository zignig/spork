from nmigen import *

from ..cores.periph import Peripheral
from ..cores.warmboot import warmboot
from ..utils.search import Enroll
from ..logger import logger

log = logger(__name__)


@Enroll(platform="ice40", provides="warmboot", device="reset_pin")
class WarmBoot(Peripheral, Elaboratable):
    def __init__(self):
        log.info("Create Warmboot Peripheral")
        super().__init__()
        bank = self.csr_bank()
        self._image = bank.csr(2, "w")
        self._en = bank.csr(1, "w")
        # expose in object so the external can be connected
        self.warm = warmboot()

    def elaborate(self, platform):
        m = Module()
        m.submodules.bridge = self._bridge
        m.submodules.warm = warm = self.warm
        # bind the signals
        m.d.sync += [warm.image.eq(self._image.w_data), warm.boot.eq(self._en.w_data)]
        return m


class FakeWarm(Peripheral, Elaboratable):
    def __init__(self):
        log.info("Create Fake Warmboot Peripheral")
        super().__init__()
        bank = self.csr_bank()
        self._image = bank.csr(2, "w")
        self._en = bank.csr(1, "w")

    def elaborate(self, platform):
        m = Module()
        m.submodules.bridge = self._bridge
        # bind the signals
        return m
