""" 
    CSR bus to attach things to stuff.
    
"""
from nmigen import *
from nmigen_soc.csr import Decoder
from nmigen_soc.csr.bus import Multiplexer, Element, Decoder
from .base import Peripheral, PeripheralBridge

from ...logger import logger

log = logger(__name__)


class RegMap:
    """mapping of the registers"""

    # TODO export in various formats

    def __init__(self):
        log.debug("Create Register Map")
        self._children = {}

    def _add_sub(self, name_list, value):
        front = name_list.pop(0)
        log.debug("%s %d", name_list, value)
        if len(name_list) == 0:
            setattr(self, front, value)
            self._children[front] = value
        else:
            if front not in self._children:
                sub_reg = RegMap()
                self._children[front] = sub_reg
                setattr(self, front, sub_reg)
                sub_reg._add_sub(name_list, value)
            else:
                sub_reg = self._children[front]
                sub_reg._add_sub(name_list, value)

    def show(self, leader=[]):
        for i in self._children:
            leader.append(i)
            lower = self._children[i]
            if isinstance(lower, RegMap):
                lower.show(leader)
            elif isinstance(lower, int):
                print(".".join(leader), lower)
            leader.pop()


class PeripheralCollection(Elaboratable):
    """Collection of peripherals to attach to a BonelessCPU"""

    def __init__(self, addr_width=16, data_width=16):
        log.debug("Create Peripheral Collection")
        self._decoder = Decoder(addr_width=addr_width, data_width=data_width)

        self.data_width = data_width
        self.mem = self._decoder.bus.memory_map
        self.devices = []
        self.map = RegMap()

        self.bus = self._decoder

        self._built = False

    def add(self, item):
        self.devices.append(item)

    def build(self):
        if not self._built:
            log.debug("Building Peripheral Collection")
            # bind and add the bus if the device does not have one
            # TODO this makes a double decoder
            # rip it out for a single bridge
            for i in self.devices:
                try:
                    self._decoder.add(i.bus)
                except NotImplementedError as e:
                    i._bridge = i.bridge(data_width=self.data_width)
                    i.bus = i._bridge.bus
                    self._decoder.add(i.bus)
            # map all the CSR devices
            for i, (start, end, width) in self.mem.all_resources():
                length = end - start
                if length > 1:
                    for j in range(length):
                        split_name = i.name.split("_")
                        last = split_name.pop()
                        last += "_" + str(j)
                        split_name.append(last)
                        self.map._add_sub(split_name, start + j)
                else:
                    self.map._add_sub(i.name.split("_"), start)
            self._built = True

    def show(self):
        self.build()
        return self.map

    def elaborate(self, platform):
        self.build()
        m = Module()
        m.submodules.bus = self._decoder
        for i in self.devices:
            m.submodules[i.name] = i
        return m
