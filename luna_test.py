from nmigen import Elaboratable, Module

from luna import top_level_cli
from luna.full_devices import USBSerialDevice

from spork.cores.periph.base import Peripheral
from spork.logger import logger

log = logger(__name__)

__all__ = ["ButtonPeripheral"]

#
# This file was :) part of LUNA.
#
# Copyright (c) 2020 Great Scott Gadgets <info@greatscottgadgets.com>
# SPDX-License-Identifier: BSD-3-Clause

""" TinyFPGA Platform definitions.

This is a non-core platform. To use it, you'll need to set your LUNA_PLATFORM variable:

    > export LUNA_PLATFORM="luna.gateware.platform.tinyfpga:TinyFPGABxPlatform"
"""

import os
import subprocess

from nmigen import (
    Elaboratable,
    ClockDomain,
    Module,
    ClockSignal,
    Instance,
    Signal,
    Const,
    ResetSignal,
)
from nmigen.build import Resource, Subsignal, Pins, Attrs, Clock, Connector, PinsN
from nmigen_boards.tinyfpga_bx import TinyFPGABXPlatform as _TinyFPGABXPlatform

from nmigen_boards.resources.interface import UARTResource
from nmigen_boards.resources.user import ButtonResources

from nmigen.build import Resource, Subsignal, Pins, Attrs
from nmigen.hdl import DomainRenamer

from fwtest import TestSpork


class TinyFPGABxDomainGenerator(Elaboratable):
    """ Creates clock domains for the TinyFPGA Bx. """

    def __init__(self, *, clock_frequencies=None, clock_signal_name=None):
        pass

    def elaborate(self, platform):
        m = Module()
        locked = Signal()

        # Create our domains...
        m.domains.sync = ClockDomain()
        m.domains.usb = ClockDomain()
        m.domains.usb_io = ClockDomain()
        m.domains.fast = ClockDomain()

        # ... create our 48 MHz IO and 12 MHz USB clock...
        clk48 = Signal()
        clk12 = Signal()
        m.submodules.pll = Instance(
            "SB_PLL40_2F_CORE",
            i_REFERENCECLK=platform.request(platform.default_clk),
            i_RESETB=Const(1),
            i_BYPASS=Const(0),
            o_PLLOUTCOREA=clk48,
            o_PLLOUTCOREB=clk12,
            o_LOCK=locked,
            # Create a 48 MHz PLL clock...
            p_FEEDBACK_PATH="SIMPLE",
            p_PLLOUT_SELECT_PORTA="GENCLK",
            p_PLLOUT_SELECT_PORTB="SHIFTREG_0deg",
            p_DIVR=0,
            p_DIVF=47,
            p_DIVQ=4,
            p_FILTER_RANGE=1,
        )

        # ... and constrain them to their new frequencies.
        platform.add_clock_constraint(clk48, 48e6)
        platform.add_clock_constraint(clk12, 12e6)

        # We'll use our 48MHz clock for everything _except_ the usb domain...
        m.d.comb += [
            ClockSignal("usb").eq(clk12),
            ClockSignal("sync").eq(clk48),
            ClockSignal("usb_io").eq(clk48),
            ClockSignal("fast").eq(clk48),
            ResetSignal("usb").eq(~locked),
            ResetSignal("sync").eq(~locked),
            ResetSignal("usb_io").eq(~locked),
            ResetSignal("fast").eq(~locked),
        ]

        return m


class TinyFPGABxPlatform(_TinyFPGABXPlatform):
    name = "TinyFPGA Bx"
    clock_domain_generator = TinyFPGABxDomainGenerator
    default_usb_connection = "usb"
    default_clk_frequency = 12e6


class USBSerialDeviceExample(Elaboratable):
    """ Device that acts as a 'USB-to-serial' loopback using our premade gateware. """

    def elaborate(self, platform):
        m = Module()

        # Generate our domain clocks/resets.
        m.submodules.car = platform.clock_domain_generator()

        # Create our USB-to-serial converter.
        ulpi = platform.request(platform.default_usb_connection)
        m.submodules.usb_serial = usb_serial = USBSerialDevice(
            bus=ulpi, idVendor=0x16d0, idProduct=0x0f3b
        )

        m.d.comb += [
            # Place the streams into a loopback configuration...
            usb_serial.tx.payload.eq(usb_serial.rx.payload),
            usb_serial.tx.valid.eq(usb_serial.rx.valid),
            usb_serial.tx.first.eq(usb_serial.rx.first),
            usb_serial.tx.last.eq(usb_serial.rx.last),
            usb_serial.rx.ready.eq(usb_serial.tx.ready),
            # ... and always connect by default.
            usb_serial.connect.eq(1),
        ]

        return m


class ACMwrap(Peripheral, Elaboratable):
    def __init__(self, tx, rx):
        log.info("USB acm CSR wrapper")
        super().__init__()
        self.tx = tx
        self.rx = rx

        bank = self.csr_bank()
        self._rx_ready = bank.csr(1, "r")
        self._rx_first = bank.csr(1, "r")
        self._rx_last = bank.csr(1, "r")
        self._rx_valid = bank.csr(1, "r")
        self._rx_payload = bank.csr(8, "r")

        self._tx_ready = bank.csr(1, "w")
        self._tx_first = bank.csr(1, "w")
        self._tx_last = bank.csr(1, "w")
        self._tx_valid = bank.csr(1, "r")
        self._tx_payload = bank.csr(8, "w")

    def elaborate(self, platform):
        m = Module()
        # Code here
        return m


from hexloader import HexLoader


class UPPER(Elaboratable):
    def __init__(self):
        pass

    def elaborate(self, platform):
        m = Module()
        acm = USBSerialDeviceExample()
        m.submodules.acm = acm

        spork = TestSpork(
            platform, uart_speed=115200, mem_size=4096, firmware=HexLoader
        )

        ts = DomainRenamer({"sync": "usb"})(spork)
        m.submodules.ts = ts

        return m


if __name__ == "__main__":
    pl = TinyFPGABxPlatform()
    pl.add_resources(
        [
            UARTResource(
                0, rx="A8", tx="B8", attrs=Attrs(IO_STANDARD="SB_LVCMOS", PULLUP=1)
            ),
            Resource("reset_pin", 0, Pins("18", conn=("gpio", 0), dir="i")),
            # *ButtonResources(pins="10", invert=True, attrs=Attrs(IO_STANDARD="SB_LVCMOS")),
        ]
    )
    construct = UPPER()
    pl.build(construct, do_program=True)
