"""
    Debouncer ( untested )
"""

__done__ = False
__working__ = False

# Switch and button debouncer

# IRC reference

# reference https://paste.debian.net/1145089/
# see https://freenode.irclog.whitequark.org/nmigen/2020-05-05#26964009

from nmigen import *
from nmigen.lib.cdc import FFSynchronizer


class Debounce(Elaboratable):
    "Debounce timer"

    def __init__(self, pin):
        self.pin = pin
        self.o = Signal()

    def elaborate(self, platform):
        m = Module()
        btn_i = Signal()

        m.submodules += FFSynchronizer(self.pin, btn_i)

        btn_r = Signal()

        timer = Signal(range(1024), reset=1023)

        with m.If(btn_i != btn_r):
            m.d.sync += btn_r.eq(btn_i)
            m.d.sync += timer.eq(timer.reset)
        with m.Elif(timer != 0):
            m.d.sync += timer.eq(timer - 1)
        with m.Else():
            m.d.sync += self.o.eq(btn_i)

        return m
