" Firmware construct , builds the sections for a working firmware "

from .base import *
import pprint
import math

from ..logger import logger
from ..upload import _crc

log = logger(__name__)
from boneless.arch.opcode import *
from boneless.arch.instr import Instr

from ..lib.stringer import Stringer
from ..lib.globals import Globals
from ..lib.commands import Command


__done__ = False


class Firmware:
    """ 
    Firmware construct 

    does initialization , main loop and library code

    this construct has a number of meta classes that will auto bind.

    SubR , Inline  , Command and strings will attch if they are used
    """

    def __init__(self, reg=None, start_window=512):
        log.info("Create Firmware Object")
        self.w = Window()
        self.sw = start_window
        self.reg = reg

        # global string set
        self.stringer = st = Stringer()

        # global variables
        self.globals = gl = Globals()

        # attach the io_map to all the subordinates
        SubR.reg = self.reg
        Inline.reg = self.reg
        Command.reg = self.reg

        # attach global string to other
        SubR.stringer = self.stringer
        Inline.stringer = self.stringer
        Command.stringer = self.stringer

        SubR.globals = gl
        Inline.globals = gl
        Command.globals = gl

        SubR.sw = start_window

        # code objects
        self.obj = []
        self._built = False
        self.fw = None
        self.hex_blob = ""

    def setup(self):
        raise FWError("No setup function")

    def prelude(self):
        log.warning("No prelude(), use to setup code")
        return []

    def instr(self):
        log.warning("There is nothing in the main loop fix instr():")
        return []

    def extra(self):
        "Add extra code/data to the firmware, override "
        return []

    def code(self):
        # Only build once, don't double allocate
        if not self._built:
            w = self.w = Window()
            self.labels = ll = LocalLabels()
            self.setup()
            self.globals.heap_pointer = 0
            fw = [
                Rem("--- Firmware Object ---"),
                Rem(self.w._name),
                L("init"),
                Rem("--- Set up the window ---"),
                MOVI(w.fp, self.sw - 8),
                STW(w.fp),
                Rem("--- Setup the heap pointer ---"),
                MOVR(R1, "end_of_data"),
                self.globals.heap_pointer(R0),
                ST(R1, R0, 0),
                Rem("--- Prelude functions ---"),
                self.prelude(),
                Rem("--- Code object setup sequence ---"),
                CodeObject.setup_list(),
                L("main"),
                [self.instr()],
                J("main"),
                ll("library_code"),
                Rem("--- Library Code ---"),
                MetaSub.code(),
                ll("extra_code"),
                Rem("--- Extra Code ---"),
                self.extra(),
                ll("data_objects"),
                Rem("--- Data Objects ---"),
                CodeObject.get_code(),
                ll("heap_start"),
                L("end_of_data"),
            ]
            self._built = True
            self.fw = fw
        else:
            fw = self.fw
        return fw

    def show(self):
        pprint.pprint(self.code(), width=1, indent=2)

    def assemble(self):
        fw = Instr.assemble(self.code())
        return fw

    def hex(self):
        def hex_string(i):
            # encode negative numbers
            if i < 0:
                # negate
                i = -i
                # set the sign bit
                i = i | (1 << 15)
            return "{:04X}".format(i)

        def pad(data):
            " pad the data to the next mod 8 integer value"
            div = 8
            l = len(data)
            extra = (1 - ((l / div) - (l // div))) * 8
            data += [0] * int(extra)
            return data

        asm = self.assemble()
        # pad the asm
        asm = pad(asm)
        # save the length
        full_hex = hex_string(len(asm))
        # append the code
        for i in asm:
            full_hex += hex_string(i)
        # append the checksum
        full_hex += hex_string(_crc(asm))
        return full_hex

    def disassemble(self):
        c = self.assemble()
        a = Assembler()
        return a.disassemble(c)
