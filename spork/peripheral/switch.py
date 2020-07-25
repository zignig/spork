" A switch builder "

# TODO , bind multiple switches

__working__ = False

from nmigen import *

from ..cores.periph.base import Peripheral
from ..cores.debounce import Debounce
from ..utils.search import Enroll

from ..logger import logger

log = logger(__name__)

__all__ = ["SwitchPeripheral"]


@Enroll(driver="switch")
class SwitchPeripheral(Peripheral, Elaboratable):
    def __init__(self):
        log.critical("Switch Unfinished")
        log.info("Create Switch Peripheral")
        super().__init__()
        bank = self.csr_bank()
        self._en = bank.csr(1, "w")
        self._button = bank.csr(16, "w")

    def elaborate(self, platform):
        m = Module()
        # Code here
        return m
