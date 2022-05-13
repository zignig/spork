# Lifted from
# https://github.com/tpwrules/tasha_and_friends/blob/master/tastaf/gateware/uart.py#L246
# Copyright (c) 2020, Thomas Watson
# With modifications

from nmigen import *
from ..cores.periph import Peripheral
from ..utils.search import Enroll

from ..logger import logger

log = logger(__name__)

__all__ = ["KermitCRC"]


@Enroll(provides="crc16")
class KermitCRC(Peripheral, Elaboratable):
    """
    Provides a cyclic redundancy check device

    This is usefull for checking code and datablocks for integrity.

    It can also be used for hash tables.

    """

    def __init__(self):
        log.info("Create Kermit CRC device")
        super().__init__()
        bank = self.csr_bank()
        # reset engine and set CRC to 0
        # the value does not matter only the write
        self.reset = bank.csr(1, "w")
        # start CRC of the given byte. will give the wrong value if engine isn't done yet!
        # this peripheral takes 8 clock cycles ( two instructions to update )

        # the given byte
        self.byte = bank.csr(8, "w")
        # the given word
        self.word = bank.csr(16, "w")
        # the crc value
        self.crc = bank.csr(16, "rw")

    def elaborate(self, platform):
        m = Module()
        m.submodules.bridge = self._bridge

        bit_counter = Signal(range(17))
        crc = Signal(16)

        with m.If(self.reset.w_stb):
            m.d.sync += [bit_counter.eq(0), crc.eq(0)]
        with m.Elif(self.byte.w_stb):
            m.d.sync += [
                bit_counter.eq(8),
                crc.eq(crc ^ self.byte.w_data),
            ]
        with m.Elif(self.word.w_stb):
            m.d.sync += [
                bit_counter.eq(16),
                crc.eq(crc ^ self.word.w_data),
            ]
        with m.If(bit_counter > 0):
            m.d.sync += [
                bit_counter.eq(bit_counter - 1),
                crc.eq((crc >> 1) ^ Mux(crc[0], 0x8408, 0)),
            ]
        with m.Elif(bit_counter == 0):
            m.d.sync += [self.crc.r_data.eq(crc)]  # , self.finished.eq(1)]
        return m
