" Example firmware"

from nmigen import *
from nmigen._unused import MustUse

from spork.cpu.boneless import BonelessSpork

from spork.cores.periph.base import Peripheral
from spork.peripheral.serial import AsyncSerialPeripheral
from spork.peripheral.timer import TimerPeripheral
from spork.peripheral.leds import LedPeripheral
from spork.peripheral.kermit_crc import KermitCRC
from spork.peripheral.warmboot import WarmBoot, FakeWarm
from spork.peripheral.watchdog import Watchdog
from spork.peripheral.profiler import Profiler
from spork.peripheral.systick import SysTick
from spork.peripheral.lsfr import LSFR
from spork.peripheral.multiply import MultiplyPeripheral

from spork.cores.ext_reset import ExternalReset
from spork.cores.debounce import Debounce

from nmigen_boards.tinyfpga_bx import TinyFPGABXPlatform
from nmigen_boards.resources.interface import UARTResource
from nmigen_boards.resources.user import ButtonResources, LEDResources

from nmigen.build import Resource, Subsignal, Pins, Attrs

from boneless.arch.opcode import Instr
from boneless.arch.opcode import *

import struct

from spork.logger import logger
from spork.upload import _crc

log = logger("root")

# silence the unused elaboratable
# this builds the to get the register map.
# so ssh, please.
MustUse._MustUse__silence = True


class TestSpork(Elaboratable):
    def __init__(
        self, platform, uart_speed=9600, mem_size=1024, firmware=None, sim=False
    ):
        self.platform = platform
        self.cpu = cpu = BonelessSpork(firmware=firmware, mem_size=mem_size)
        self.sim = sim
        self.firmware = firmware
        self.mem_size = mem_size

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

        # timer2 = TimerPeripheral(32)
        # cpu.add_peripheral(timer2)

        # A blinky thing
        led = platform.request("led")
        statusled = LedPeripheral(led)
        cpu.add_peripheral(statusled)

        # CRC engine, !! HAZARD, this needs a NOP to get a correct reading!!!
        crc = KermitCRC()
        cpu.add_peripheral(crc)

        # System Ticker
        systick = SysTick(0xFFFF)
        cpu.add_peripheral(systick)
        # Reg test

        multiply = MultiplyPeripheral()
        cpu.add_peripheral(multiply)
        # LSFR

        lsfr = LSFR()
        cpu.add_peripheral(lsfr)

        watchdog = Watchdog(cpu.cpu)
        cpu.add_peripheral(watchdog)

        # Profiler
        # pro = Profiler()
        # cpu.add_peripheral(pro)

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
            self.er = ExternalReset(
                wb.select, wb.ext_image, wb.ext_boot, dtr, debug=False
            )
        # else:
        #    warm = FakeWarm()
        #    cpu.add_peripheral(warm)

        # build the register map

    def build(self):
        self.cpu.build()
        # Attach the firmware
        if self.firmware is not None:
            f = self.firmware(self.cpu.map, start_window=self.mem_size)
            self.fw = f
            # Sporkify it !
            self.cpu.firmware(f.code())
            self.hex_blob = f.hex()

    def elaborate(self, platform):
        m = Module()
        # Attach the cpu
        m.submodules.cpu = self.cpu
        # Attach the external reset
        if not self.sim:
            m.submodules.external_reset = self.er
        # Attache the debouncer
        return m


# from echo_fw import Echo
from hexloader import HexLoader

# from bootloader import Bootloader
from nmigen.hdl.ir import UnusedElaboratable

FIRM = HexLoader

# TODO this needs to be moved into the spork
def build(TheFirmware, mem_size=1024 * 6, sim=False, detail=False):
    # for programming from a firmware file
    if detail:
        print("Testing Spork")
    # TODO abstract this plaform set
    platform = TinyFPGABXPlatform()
    # FTDI on the tinybx
    platform.add_resources(
        [
            UARTResource(
                0, rx="A8", tx="B8", attrs=Attrs(IO_STANDARD="SB_LVCMOS", PULLUP=1)
            ),
            Resource(
                "reset_pin", 0, Pins("A9", dir="i"), Attrs(IO_STANDARD="SB_LVCMOS")
            ),
            # *ButtonResources(pins="10", invert=True, attrs=Attrs(IO_STANDARD="SB_LVCMOS")),
            *LEDResources(
                "blinky", pins="J1 H2 H9 D9", attrs=Attrs(IO_STANDARD="SB_LVCMOS")
            ),
        ]
    )

    # Spork it up
    spork = TestSpork(platform, uart_speed=115200, mem_size=mem_size, sim=sim)

    # Build the firmware
    spork.build()
    # if detail:
    #    print(spork.cpu.map.show())

    f = TheFirmware(spork.cpu.map, start_window=mem_size)
    spork.fw = f
    # if detail:
    #    f.show()
    # Sporkify it !
    code = f.code()
    spork.cpu.firmware(code)
    # if detail:
    #    print(f.hex())
    spork.hex_blob = f.hex()
    return spork


# TODO this main needs to be moved below the spork.

if __name__ == "__main__":
    Elaboratable._Elaboratable__silence = True
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--program", action="store_true")
    parser.add_argument("-l", "--list", action="store_true")
    parser.add_argument("-s", "--simulate", action="store_true")
    parser.add_argument("-g", "--generate", action="store_true")
    args = parser.parse_args()

    fw = FIRM  # use this firmware

    if args.simulate:
        spork = build(fw, mem_size=1024)
        from nmigen.sim import Simulator
        from scratchpad.sim_data import test_rx, str_data

        st = "sphinx of black quartz judge my vow"
        # print(hex(_crc(st.encode("utf-8"))))
        data = str_data(st)
        dut = spork.cpu.pc.devices[0]._phy
        dut.divisor_val = spork.divisor
        sim = Simulator(spork)
        sim.add_clock(1e-3)
        sim.add_sync_process(test_rx(data, dut))
        with sim.write_vcd("sim.vcd"):
            sim.run()

    if args.list:
        spork = build(fw, detail=True)

    if args.program:
        spork = build(fw, detail=True)
        spork.platform.build(spork, do_program=True)

    if args.generate:
        spork = build(fw, mem_size=1024, sim=True)
        from nmigen.back import cxxrtl
        from nmigen.hdl import ir

        # output = rtlil.convert(
        #    spork, name="cxx.il", ports=[spork.cpu.pc.devices[0]._phy.tx.o]
        # )
        frag = ir.Fragment.get(spork, spork.platform).prepare()
        output, name_map = cxxrtl.convert_fragment(frag)
        print(name_map)
        f = open("../cxxrtl_sim/boneless.sim.cpp", "w")
        f.write(output)
        f.close()
