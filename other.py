# Spork templated file
# Created on Tue May 19 18:54:38 2020
# Empty Board file

from nmigen import *
from ideal_spork.boards.extra_boards.zignig_dev import zignig_dev


class other(Elaboratable):
    def __init__(self, platform):
        # Add some resources
        platform.add_resources([])

    def elaborate(self, platform):
        m = Module()
        # Code here
        return m


if __name__ == "__main__":
    platform = zignig_dev()
    dut = other(platform)

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--program", action="store_true")
    parser.add_argument("-s", "--simulate", action="store_true")
    args = parser.parse_args()

    if args.simulate:
        from nmigen.cli import pysim

        with pysim.Simulator(dut, vcd_file=open("view_other.vcd", "w")) as sim:
            sim.add_clock(1e-3)
            sim.run_until(1000, run_passive=True)

    if args.program:
        platform.build(dut, do_program=True)
