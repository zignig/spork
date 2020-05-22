# Spork templated file
# Created on Tue May 19 19:47:47 2020

from nmigen import *
from ideal_spork.boards.extra_boards.zignig_dev import zignig_dev


# Extra imports
from ideal_spork.peripheral.switch import SwitchPeripheral
from ideal_spork.peripheral.leds import LedPeripheral
from ideal_spork.peripheral.serial import AsyncSerialPeripheral
from ideal_spork.peripheral.button import ButtonPeripheral


class testing(Elaboratable):
    def __init__(self, platform, firmware=None, mem_size=512):

        self.platform = platform

        self.cpu = cpu = BonelessSpork(firmware=firmware, mem_size=mem_size)

    def elaborate(self, platform):
        m = Module()
        # Attach the cpu
        m.submodules.cpu = self.cpu
        # Attach the external reset
        return m


if __name__ == "__main__":
    platform = zignig_dev()
    dut = testing(platform)

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--program", action="store_true")
    parser.add_argument("-s", "--simulate", action="store_true")
    args = parser.parse_args()

    if args.simulate:
        from nmigen.cli import pysim

        with pysim.Simulator(dut, vcd_file=open("view_testing.vcd", "w")) as sim:
            sim.add_clock(1e-3)
            sim.run_until(1000, run_passive=True)

    if args.program:
        platform.build(dut, do_program=True)
