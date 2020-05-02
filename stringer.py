# stored string handling functions

from ideal_spork.firmware.base import *
from ideal_spork.logger import logger

log = logger(__name__)


class Stringer(CodeObject):
    def __init__(self):
        super().__init__()
        self.strings = {}

    def __iadd__(self, item):
        print(item)

    def code(self):
        log.critical("Unfinished")
        return [Rem("String code object goes here"), [0]]
