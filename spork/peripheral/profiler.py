from nmigen import *

from ..cores.periph.base import Peripheral
from ..utils.search import Enroll

from ..logger import logger

log = logger(__name__)

__all__ = ["Profiler"]

__working__ = False


class Stat(Elaboratable):
    def __init__(self):
        self.val = Signal(16)

    def elaborate(self, platform):
        m = Module()
        return m


@Enroll(provides="profiler")
class Profiler(Peripheral, Elaboratable):
    """
    Basic Profiler

    """

    def __init__(self, count=16):
        log.info("Create Profiler Peripheral")
        super().__init__()
        self.count = count
        bank = self.csr_bank()
        self._en = bank.csr(1, "rw")
        self.addr = bank.csr(16, "rw")

    def elaborate(self, platform):
        m = Module()
        m.submodules.bridge = self._bridge
        stats = []
        for i in range(self.count):
            log.critical("create prof")
            s = Stat()
            stats.append(s)
            m.submodules["stat_" + str(i)] = s

        return m
