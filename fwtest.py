" Example firmware"

from nmigen import *

from ideal_spork.cpu.boneless import BonelessSpork

from ideal_spork.peripheral.serial import AsyncSerialPeripheral
from ideal_spork.peripheral.timer import TimerPeripheral
from ideal_spork.peripheral.leds import LedPeripheral
from ideal_spork.peripheral.kermit_crc import KermitCRC
from ideal_spork.peripheral.warmboot import WarmBoot, FakeWarm

from ideal_spork.cores.ext_reset import ExternalReset
from ideal_spork.cores.debounce import Debounce

from nmigen_boards.tinyfpga_bx import TinyFPGABXPlatform
from nmigen_boards.resources.interface import UARTResource
from nmigen_boards.resources.user import ButtonResources

from nmigen.build import Resource, Subsignal, Pins, Attrs

from boneless.arch.opcode import Instr
from boneless.arch.opcode import *

import struct
import crcmod.predefined

crc_16_kermit = crcmod.predefined.mkPredefinedCrcFun("kermit")


class TestSpork(Elaboratable):
    def __init__(
        self, platform, uart_speed=9600, mem_size=512, firmware=None, sim=False
    ):
        self.platform = platform
        self.cpu = cpu = BonelessSpork(firmware=firmware, mem_size=mem_size)
        self.sim = sim

        # Request a uart at speed from the platform
        uart = platform.request("uart")
        uart_divisor = int(platform.default_clk_frequency // uart_speed)
        self.divisor = uart_divisor

        # Make the peripheral
        serial = AsyncSerialPeripheral(pins=uart, divisor=uart_divisor)
        # Attach it to the CPU
        cpu.add_peripheral(serial)

        # A countdown timer with interrupt
        timer = TimerPeripheral(32)
        cpu.add_peripheral(timer)

        # A blinky thing
        led = platform.request("led")
        statusled = LedPeripheral(led)
        cpu.add_peripheral(statusled)

        # CRC engine, !! HAZARD, this needs a NOP to get a correct reading!!!
        crc = KermitCRC()
        cpu.add_peripheral(crc)

        if sim == False:
            # ice40 warmboot device
            warm = WarmBoot()
            cpu.add_peripheral(warm)

            # Semi external device to reset on an out of band pin
            # DTR on FTDI, 4 toggles -> warmboot , 7 toggles bootloader
            # within a timeout.

            # add the external interface for the warmboot
            # runs off the DTR pin of the FTDI
            dtr = platform.request("reset_pin")
            # the warmboot instance
            wb = warm.warm
            self.er = ExternalReset(wb.select, wb.ext_image, wb.ext_boot, dtr)
        else:
            warm = FakeWarm()
            cpu.add_peripheral(warm)

        # build the register map
        cpu.build()

    def elaborate(self, platform):
        m = Module()
        # Attach the cpu
        m.submodules.cpu = self.cpu
        # Attach the external reset
        if not self.sim:
            m.submodules.external_reset = self.er
        # Attache the debouncer
        return m


from echo_fw import Echo
from bootloader import Bootloader


def build(TheFirmware, mem_size=512, sim=False):
    # for programming from a firmware file
    print("Testing Spork")
    platform = TinyFPGABXPlatform()
    # FTDI on the tinybx
    platform.add_resources(
        [
            UARTResource(
                0, rx="A8", tx="B8", attrs=Attrs(IO_STANDARD="SB_LVCMOS", PULLUP=1)
            ),
            Resource("reset_pin", 0, Pins("18", conn=("gpio", 0), dir="i")),
            # *ButtonResources(pins="10", invert=True, attrs=Attrs(IO_STANDARD="SB_LVCMOS")),
        ]
    )
    # print(platform.resources)
    # Spork it up
    spork = TestSpork(platform, uart_speed=115200, mem_size=mem_size, sim=sim)
    # Build the firmware
    print(spork.cpu.map.show())
    f = TheFirmware(spork.cpu.map, start_window=mem_size)
    spork.fw = f
    f.show()
    # Sporkify it !
    spork.cpu.firmware(f.code())
    print(len(f.assemble()), f.hex())
    return spork


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--program", action="store_true")
    parser.add_argument("-s", "--simulate", action="store_true")
    parser.add_argument("-g", "--generate", action="store_true")
    args = parser.parse_args()

    if args.simulate:
        spork = build(Bootloader, mem_size=1024)
        from nmigen.cli import pysim
        from sim_data import test_rx, str_data

        st = "sphinx of black quartz judge my vow"
        print(hex(crc_16_kermit(st.encode("utf-8"))))
        data = str_data(st)
        dut = spork.cpu.pc.devices[0]._phy
        dut.divisor_val = spork.divisor
        with pysim.Simulator(spork, vcd_file=open("view_spork.vcd", "w")) as sim:
            sim.add_clock(1e-3)
            sim.add_sync_process(test_rx(data, dut))
            sim.run_until(1000, run_passive=True)

    if args.program:
        spork = build(Bootloader, mem_size=1024)
        spork.platform.build(spork, do_program=True)

    if args.generate:
        spork = build(Bootloader, mem_size=1024, sim=True)
        from nmigen.back import rtlil, verilog, pysim

        output = rtlil.convert(
            spork, name="cxx.il", ports=[spork.cpu.pc.devices[0]._phy.tx.o]
        )
        f = open("../cxxrtl_sim/cxx.il", "w")
        f.write(output)
        f.close()
