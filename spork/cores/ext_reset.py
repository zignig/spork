"""
    A device to remotely reset the FPGA

    Attached to the DTR of the serial port.

    Waggle the DTR pin within the timeout and it will perform an action.
    
"""

from nmigen import *
import itertools

from nmigen.build import Resource, Subsignal, Pins
from nmigen.build import ResourceError

from ..logger import logger

log = logger(__name__)

# external reset ( used on DTR pin )
# count the pin toggles within the timeout
# warm boot based on count


class ExternalReset(Elaboratable):
    def __init__(self, select, image, boot, pin, debug=False):
        log.debug("Create External Reset")
        self.select = select
        self.image = image
        self.boot = boot
        self.pin = pin
        self.timeout = int(12e6)
        self.debug = debug

    def elaborate(self, platform):
        m = Module()

        counter = Signal(48)
        enable = Signal()  # enable the counter
        current = Signal()  # get the current pin state
        toggle_count = Signal(5)  # count the pin toggles

        # this module is being weird debug with leds
        def get_all_resources(name):
            resources = []
            for number in itertools.count():
                try:
                    resources.append(platform.request(name, number))
                except ResourceError:
                    break
            return resources

        # IF debug is on grab all the blinky
        if self.debug:
            leds = [res.o for res in get_all_resources("blinky")]
            self.leds = Cat(led for led in leds)
            log.critical(leds)

        with m.If(enable == 1):
            m.d.sync += counter.eq(counter + 1)

        with m.FSM() as fsm:
            with m.State("INIT"):
                # get the current pin state
                m.d.sync += current.eq(self.pin)
                # reset everything
                m.d.sync += self.select.eq(0)
                m.d.sync += enable.eq(0)
                m.d.sync += counter.eq(0)
                m.d.sync += toggle_count.eq(0)
                if self.debug:
                    m.d.sync += self.leds.eq(16)
                m.next = "START"

            with m.State("START"):
                # if the pin state has changed
                with m.If(self.pin != current):
                    # start the counter
                    m.d.sync += toggle_count.eq(toggle_count + 1)
                    m.d.sync += enable.eq(1)
                    # save the new state
                    m.d.sync += current.eq(self.pin)
                    m.next = "COUNT"
                with m.If(counter == self.timeout):
                    m.next = "CHOOSE"

            with m.State("COUNT"):
                # count the toggles
                with m.If(self.pin != current):
                    m.d.sync += toggle_count.eq(toggle_count + 1)
                    if self.debug:
                        m.d.sync += self.leds.eq(toggle_count)
                    m.next = "NEXT"
                with m.If(counter == self.timeout):
                    m.d.sync += self.select.eq(1)
                    m.next = "CHOOSE"

            with m.State("NEXT"):
                m.d.sync += current.eq(self.pin)
                if self.debug:
                    m.d.sync += self.leds.eq(16)
                m.next = "COUNT"

            with m.State("CHOOSE"):
                # switch the warmboot to external
                # select the image count based on toggles
                # m.d.sync += self.select.eq(1)
                with m.Switch(toggle_count):
                    with m.Case(4):
                        m.next = "IMAGE1"
                    with m.Case(8):
                        m.next = "IMAGE2"
                    with m.Default():
                        m.next = "INIT"
                # ? 7 reset the boneless ?

            with m.State("IMAGE1"):
                # select image 0
                m.d.sync += self.image.eq(0)
                m.next = "WARMBOOT"

            with m.State("IMAGE2"):
                # select image 1
                m.d.sync += self.image.eq(1)
                m.next = "WARMBOOT"

            with m.State("WARMBOOT"):
                # warmboot
                m.d.sync += self.boot.eq(1)
        return m
