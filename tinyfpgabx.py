" Example spork "

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


def Firmware(reg):
    print(reg)
    return [
        # enable the led
        MOVI(R0, 1),
        STXA(R0, reg.status_led_en),
        # load the timer
        MOVI(R0, 0x8FF),
        STXA(R0, reg.timer_reload),
        # enable timer and events
        MOVI(R0, 1),
        STXA(R0, reg.timer_en),
        STXA(R0, reg.timer_ev_enable),
        # reset the crc
        MOVI(R0, 1),
        STXA(R0, reg.crc_reset),
        # led is on R2
        MOVI(R2,1),
        L("main_loop"),
            LDXA(R0,reg.timer_ev_pending),
            CMPI(R0,1),
            BZ1("blink"),
            LDXA(R0,reg.serial_rx_rdy),
            CMPI(R0,1),
            BZ1("echo"),
        J("main_loop"),

        L("blink"),
            MOVI(R0,1),
            STXA(R0,reg.timer_ev_pending),
            XORI(R2,R2,0xFFFF),
            STXA(R2,reg.status_led_led),
        J("main_loop"),

        L("echo"),
            LDXA(R3,reg.serial_rx_data),
            STXA(R3,reg.crc_byte),
            STXA(R3,reg.serial_tx_data),    
        J("main_loop"),
    ]


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
    spork = TestSpork(platform)

    f = Firmware(spork.cpu.map)
    spork.cpu.firmware(f)

    from nmigen.cli import pysim
    from sim_data import test_rx, str_data 
    st = "sphinx of black quartz judge my vow"
    st = "testing"
    print(hex(crc_16_kermit(st.encode('utf-8'))))
    data = str_data(st)
    dut = spork.cpu.pc.devices[0]._phy
    dut.divisor_val  = spork.divisor
    #with pysim.Simulator(spork, vcd_file=open("view_spork.vcd", "w")) as sim:
    #    sim.add_clock(0.1)
    #    sim.add_sync_process(test_rx(data,dut))
    #    sim.run_until(10000, run_passive=True)
    platform.build(spork,do_program=True)
