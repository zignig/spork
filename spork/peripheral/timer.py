"""
    General purpose timer with events.
    
"""
from nmigen import *

from ..cores.periph.base import Peripheral
from ..utils.search import Enroll

from ..logger import logger

log = logger(__name__)

__all__ = ["TimerPeripheral"]
__working__ = True


@Enroll(provides="timer")
class TimerPeripheral(Peripheral, Elaboratable):
    """Timer peripheral.

    A general purpose down-counting timer peripheral.

    CSR registers
    -------------
    reload : read/write
        Reload value of counter. When `ctr` reaches 0, it is automatically reloaded with this value.
    en : read/write
        Counter enable.
    ctr : read/write
        Counter value.

    Events
    ------
    zero : edge-triggered (rising)
        Counter value reached 0.

    Parameters
    ----------
    width : int
        Counter width.

    Attributes
    ----------
    bus : :class:`nmigen_soc.wishbone.Interface`
        Wishbone bus interface.
    irq : :class:`IRQLine`
        Interrupt request.
    """

    def __init__(self, width, name=None):
        log.info("Create Timer Peripheral")
        super().__init__(name=name)

        if not isinstance(width, int) or width < 0:
            raise ValueError(
                "Counter width must be a non-negative integer, not {!r}".format(width)
            )
        if width > 32:
            raise ValueError(
                "Counter width cannot be greater than 32 (was: {})".format(width)
            )
        self.width = width

        bank = self.csr_bank()
        self._reload = bank.csr(width, "rw")
        self._en = bank.csr(1, "rw")
        self._ctr = bank.csr(width, "rw")

        self._zero_ev = self.event(mode="rise")

    def elaborate(self, platform):
        m = Module()
        m.submodules.bridge = self._bridge

        with m.If(self._en.r_data):
            with m.If(self._ctr.r_data == 0):
                m.d.comb += self._zero_ev.stb.eq(1)
                m.d.sync += self._ctr.r_data.eq(self._reload.r_data)
            with m.Else():
                m.d.sync += self._ctr.r_data.eq(self._ctr.r_data - 1)

        with m.If(self._reload.w_stb):
            m.d.sync += self._reload.r_data.eq(self._reload.w_data)
        with m.If(self._en.w_stb):
            m.d.sync += self._en.r_data.eq(self._en.w_data)
        with m.If(self._ctr.w_stb):
            m.d.sync += self._ctr.r_data.eq(self._ctr.w_data)

        return m
