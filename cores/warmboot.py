from nmigen import *

from ..logger import logger

log = logger(__name__)


class warmboot(Elaboratable):
    def __init__(self):
        log.debug("Create Warmboot")
        self.image = Signal(2, reset=1)
        self.boot = Signal()
        self.ext_boot = Signal()
        self.ext_image = Signal(2)
        self.select = Signal()

    def elaborate(self, platform):
        m = Module()
        image_internal = Signal(2)
        boot_internal = Signal()
        m.submodules.wb = Instance(
            "SB_WARMBOOT",
            i_S1=image_internal[1],
            i_S0=image_internal[0],
            i_BOOT=boot_internal,
        )
        m.d.comb += [
            image_internal.eq(Mux(self.select, self.ext_image, self.image)),
            boot_internal.eq(Mux(self.select, self.ext_boot, self.boot)),
        ]
        return m
