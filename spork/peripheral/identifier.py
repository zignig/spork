"""
    Creates a 128 bit id for the device , read only.
"""

from nmigen import *

from ..cores.periph import Peripheral
from ..utils.search import Enroll

from ..logger import logger

log = logger(__name__)

import uuid

__working__ = False


@Enroll(provides="identifier")
class Identifier(Peripheral, Elaboratable):
    def __init__(self, base="unsafe_default"):
        log.info("Create Id Object")
        super().__init__()
        bank = self.csr_bank()

        self.uuid = str(uuid.uuid4())
        self.length = len(self.uuid)

        self.get = bank.csr(1, "r")
        self.counter = Signal()
        self.reset = Signal()

    def elaborate(self, platform):
        m = Module()
        m.submodules.bridge = self._bridge

        # CODE

        return m
