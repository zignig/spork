" Example firmware"

from nmigen import *
from ideal_spork.cpu.boneless import BonelessSpork

from ideal_spork.peripheral.serial import AsyncSerialPeripheral
from ideal_spork.peripheral.timer import TimerPeripheral
from ideal_spork.peripheral.leds import LedPeripheral
from ideal_spork.peripheral.kermit_crc import KermitCRC

from nmigen_boards.tinyfpga_bx import TinyFPGABXPlatform
from nmigen_boards.resources.interface import UARTResource
from nmigen.build import Resource, Subsignal, Pins, Attrs

from boneless.arch.opcode import Instr
from boneless.arch.opcode import *

import struct
import crcmod.predefined

crc_16_kermit = crcmod.predefined.mkPredefinedCrcFun("kermit")


class TestSpork(Elaboratable):
    def __init__(self, platform, mem_size=512, firmware=None):
        self.cpu = cpu = BonelessSpork(firmware=firmware, mem_size=mem_size)

        uart = platform.request("uart")
        uart_divisor = int(platform.default_clk_frequency // 115200)
        self.divisor = uart_divisor

        serial = AsyncSerialPeripheral(pins=uart, divisor=uart_divisor)
        cpu.add_peripheral(serial)

        timer = TimerPeripheral(16)
        cpu.add_peripheral(timer)

        led = platform.request("led")
        status_led = LedPeripheral(led)
        cpu.add_peripheral(status_led)

        crc = KermitCRC()
        cpu.add_peripheral(crc)

        # build the register map
        cpu.build()

    def elaborate(self, platform):
        m = Module()
        m.submodules.cpu = self.cpu
        return m


from echo_fw import Echo


if __name__ == "__main__":
    print("Testing Spork")
    platform = TinyFPGABXPlatform()
    # FTDI on the tinybx
    platform.add_resources(
        [
            UARTResource(
                0, rx="A8", tx="B8", attrs=Attrs(IO_STANDARD="SB_LVCMOS", PULLUP=1)
            )
        ]
    )
    # Spork it up
    spork = TestSpork(platform)
    # Build the firmware
    print(spork.cpu.map)
    f = Echo(spork.cpu.map)
    f.show()
    # Sporkify it !
    spork.cpu.firmware(f.code())

    from nmigen.cli import pysim
    from sim_data import test_rx, str_data

    st = "sphinx of black quartz judge my vow"
    print(hex(crc_16_kermit(st.encode("utf-8"))))
    data = str_data(st)
    dut = spork.cpu.pc.devices[0]._phy
    dut.divisor_val = spork.divisor
    with pysim.Simulator(spork, vcd_file=open("view_spork.vcd", "w")) as sim:
        sim.add_clock(0.1)
        sim.add_sync_process(test_rx(data, dut))
        sim.run_until(10000, run_passive=True)
    # platform.build(spork,do_program=True)
