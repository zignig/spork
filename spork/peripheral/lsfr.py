"""
Linear feedback shift register
"""

from nmigen import *

from functools import reduce
from operator import xor


from ..cores.periph.base import Peripheral
from ..utils.search import Enroll

from ..logger import logger

log = logger(__name__)

__all__ = ["LSFR"]

# https://users.ece.cmu.edu/~koopman/lfsr/16.txt
# for max lenth sequences
def get_taps(mls):
    "takes a hex value and turns it into taps"
    bin_string = bin(mls)[2:]
    taps = []
    for i, j in enumerate(reversed(bin_string)):
        if j == "1":
            taps.append(i)
    return taps


@Enroll(provides="lsfr")
class LSFR(Peripheral, Elaboratable):
    """
    Linear Feedback Shift register
    """

    def __init__(self, initial=1, start_taps=0x83BC):
        log.info("Create LSFR Peripheral")
        super().__init__()
        self.SIZE = 16
        assert initial != 0
        self.initial = initial
        self.initial_taps = start_taps
        bank = self.csr_bank()

        self.value = bank.csr(self.SIZE, "rw")
        self.taps = bank.csr(self.SIZE, "rw")
        self.mode = bank.csr(1, "rw")  # 0 , free running

        self.current = Signal(self.SIZE)

        self.taps_internal = Signal(self.SIZE)
        self.incr = Signal()  #
        self.startup = Signal()
        self.match = Signal(self.SIZE)

    def elaborate(self, platform):
        m = Module()
        # Remember to attach the bridge
        m.submodules.bridge = self._bridge
        # the lsfr counter
        # mode 0 , free running values
        # mode 1 , increment per read
        out = Signal()  # the output bit
        # make all the internal taps and with the data
        m.d.comb += self.match.eq(self.taps_internal & self.value.r_data)
        # create an XOR monster that binds unused taps
        # I _think_ that it will work out
        m.d.comb += out.eq(~reduce(xor, [self.match[i] for i in range(self.SIZE)]))

        with m.If(self.startup == 0):
            m.d.sync += self.taps_internal.eq(self.initial_taps)
            m.d.sync += self.value.r_data.eq(self.initial)
            m.d.sync += self.current.eq(self.initial)
            m.d.sync += self.mode.r_data.eq(1)
            # disable the initialize
            m.d.sync += self.incr.eq(1)
            m.d.sync += self.startup.eq(1)
        with m.Else():
            with m.If(self.value.r_stb):
                m.d.sync += self.value.r_data.eq(self.current)
                m.d.sync += self.incr.eq(1)
            with m.If(self.incr == 1):  # increment
                m.d.sync += Cat(self.current).eq(Cat(out, self.current))
                with m.If(self.mode.r_data == 1):
                    m.d.sync += self.incr.eq(1)
                with m.Else():
                    m.d.sync += self.incr.eq(
                        0
                    )  # stop the next update until read strobe

        # update the registers with a write
        with m.If(self.taps.w_stb):
            # taps are readonly ( so it can be hidden )
            m.d.sync += self.taps_internal.eq(self.taps.w_data)
        with m.If(self.mode.w_stb):
            m.d.sync += self.mode.r_data.eq(self.mode.w_data)
        with m.If(self.value.w_stb):
            # m.d.sync += self.value.r_data.eq(self.value.w_data)
            m.d.sync += self.current.eq(self.value.w_data)
        return m


if __name__ == "__main__":
    val = get_taps(0x83BC)
    print(val)
