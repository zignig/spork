"""
Linear feedback shift register

A device that will return a psuedorandom random bitstream.

https://en.wikipedia.org/wiki/Linear-feedback_shift_register

16 bits, configurable.

can be used for randomish data and terriblee encryption.

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
# for max length sequences
# 8016,801C,801F,8029,805E,806B,8097,809E,80A7,80AE,80CB,80D0,80D6,80DF,80E3,810A,810C,8112


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

    def __init__(self, initial=0xCAFE, start_taps=0x83BC):
        log.info("Create LSFR Peripheral")
        super().__init__()
        self.SIZE = 16
        assert initial != 0

        self.initial = initial
        self.initial_taps = start_taps

        bank = self.csr_bank()

        self.value = bank.csr(self.SIZE, "rw")
        self.taps = bank.csr(self.SIZE, "rw")
        self.mode = bank.csr(1, "rw")  # 0 :free running , 1 increment on read

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
        # make all the internal taps AND with the data
        m.d.comb += self.match.eq(self.taps_internal & self.current)
        # create an XOR monster that binds all taps . zeros propagate
        # I _think_ that it will work out
        m.d.comb += out.eq(~reduce(xor, [self.match[i] for i in range(self.SIZE)]))

        with m.FSM() as fsm:
            with m.State("INIT"):
                m.d.sync += self.taps_internal.eq(self.initial_taps)
                m.d.sync += self.value.r_data.eq(self.initial)
                m.d.sync += self.current.eq(self.initial)
                m.d.sync += self.mode.r_data.eq(0)
                # disable the initialize
                m.d.sync += self.incr.eq(1)
                m.d.sync += self.startup.eq(1)
                m.next = "INCREMENT"

            with m.State("INCREMENT"):
                # advance the lsfr
                m.d.sync += Cat(self.current).eq(Cat(out, self.current))
                m.next = "MAYBEWAIT"

            with m.State("MAYBEWAIT"):
                m.d.sync += self.value.r_data.eq(self.current)
                with m.If(self.mode.r_data == 1):
                    # mode = 1 , increment on read
                    with m.If(self.value.r_stb):
                        m.next = "INCREMENT"
                with m.Else():
                    # mode = 0 , free running
                    m.next = "INCREMENT"

        # update the registers with a write
        with m.If(self.taps.w_stb):
            # taps are readonly ( so it can be hidden )
            m.d.sync += self.taps_internal.eq(self.taps.w_data)
        with m.If(self.mode.w_stb):
            m.d.sync += self.mode.r_data.eq(self.mode.w_data)
        with m.If(self.value.w_stb):
            m.d.sync += self.value.r_data.eq(self.value.w_data)
            m.d.sync += self.current.eq(self.value.w_data)
        return m


if __name__ == "__main__":
    val = get_taps(0x83BC)
    print(val)
