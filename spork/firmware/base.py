"""

This is the base file for creating subcomponents for the firmware.

The main aim is to only add components to the firmware if they are 
actually used in the program, otherwise they are not included.

"""

from collections import OrderedDict
import random
import pprint
import weakref

from ..cores.periph.bus import RegMap

from ..logger import logger

log = logger(__name__)

__all__ = [
    "LocalLabels",
    "SubR",
    "Window",
    "MetaSub",
    "Rem",
    "CodeObject",
    "Inline",
    "FWError",
    "Ref",
]

__done__ = False
__working__ = True

"""
Overview

Ideas

Allocate variables into a register bank, break it into windows 
limit the total number of windows and spill into ram if needed
, it's all flat ram in the boneless , minimise EXTI...

Work out how to make sure that the variables are in the correct window
for actions 

Minimise the amount of spill an copying from one window to the other

? contiguous windows
? linked list of windows
? dynamic window allocation

multi register allocations ? 
pointer deferencing ? 

###

from conversations with tpwrules and looking at his programming style.
The use of a frame stack where each subroutine call moves the register window 
up 8 registers.

- Loads the needed registers from the preceeding frame
- Allocates local variables 
- Runs the subroutine code
- And then return jumps from the parent frame.
- The parent routine can then pluck register values out of the child frame.

This is quite elegant. A subroutine becomes.

assuming R6 is the Frame pointer (fp)

If you need to pass variables up and down

    LD(var1,fp,1) # load the first register of the previous frame into var1 
    LD(var2,fp,2) # second register
    ADJW(-8) # move the window up 
    LDW(fp,-8) # put the previous window address into R6

    # other code
    # blah blah blah


    Then return up
    ADJW(8) # move the window to the previous frame address
    JR(R7,0) # the return jump is in the parent frame

    ST(return_val,fp,-3) # put the value it register 3 in the frame above

If nothing needs to be passed up or down

    ADJW(8)
    # blah blah blah 
    ADJW(-8)
    JR(R7,0)

and you don't lose a register for the frame pointer.

When you want to call a subroutine , it's just

    JAL(R7,'subroutine')

and tada, it runs and makes the registers available to the above frame.

Kind of nifty.

rehack of https://github.com/tpwrules/ice_panel/blob/master/bonetools.py

"""

from boneless.arch.opcode import *
from boneless.arch.instr import Instr


class RegError(Exception):
    pass


class NameCollision(RegError):
    pass


class WindowFull(RegError):
    pass


class BadParamCount(RegError):
    pass


class FWError(Exception):
    pass


class Ref:
    """Create a reference to another symbol
    assembler will make this into a absolute integer reference to the label
    """

    def __init__(self, name):
        self.name = name

    def __call__(self, name):
        def relocate(resolver):
            return resolver(self.name)

        return relocate

    def __repr__(self):
        return 'Ref("' + str(self.name) + '")'


class PostFix:
    _postfixes = []
    _post_counter = 0

    def __init__(self):
        self.postfix = None

    def __call__(self, postfix=None, bits=16):
        counter = 0
        while True:
            if not postfix:
                postfix = "_{:04X}".format(PostFix._post_counter)
                PostFix._post_counter += 1
            if postfix not in PostFix._postfixes:
                PostFix._postfixes += postfix
                return postfix
            counter += 1
            # guard
            if counter > 100:
                raise FWError("Too many prefixes %s", postfix)


# a postfix generator
Postfix = PostFix()

import weakref


class CodeObject:
    "For adding data objects to the firmware"
    _ItemCounter = 0  # used for ordering in the firmware
    _objects = set()

    def __init__(self):
        # log.critical("build " + str(self))
        CodeObject._ItemCounter += 1
        CodeObject._objects.add(weakref.ref(self))
        object.__setattr__(self, "_postfix", Postfix())
        object.__setattr__(self, "pos", int(CodeObject._ItemCounter))

    def __lt__(self, other):
        return self.pos < other.pos

    def __repr__(self):
        return str("\t" + self.__class__.__name__)

    def build(self):
        log.warning("No build for " + str(self))

    def setup(self):
        return []

    @classmethod
    def setup_list(cls):
        log.info("Setup the Code Objects")
        li = [Rem("Setup the Code Objects")]
        o = list(cls._scan())
        o.sort()
        for i in o:
            s = i.setup()
            if len(s) > 0:
                li += [Rem(str(i)), s]
        log.info("End Setup Code")
        return li

    @classmethod
    def _scan(cls):
        log.info("Scan")
        dead = set()
        for ref in cls._objects:
            obj = ref()
            if obj is not None:
                # log.info("\t" + str(obj))
                # log.critical(obj)
                yield obj
            else:
                dead.add(ref)
        cls._objects -= dead

    @classmethod
    def get_code(cls):
        l = []
        o = []
        o = list(cls._scan())
        o.sort()
        log.info("Data Objects")
        for i in o:
            log.info(i)
            l += [i.code()]
        return l


class Inline:
    "Define an inline function"

    def __init__(self, window, ll=None):
        self.w = window
        if ll is not None:
            self.ll = ll
        else:
            self.ll = LocalLabels()

    def instr(self):
        raise FWError("Inline class needs 'instr' defined return a [] of asm")

    def __call__(self):
        return self.instr()


class Rem:
    "for adding remarks in code"

    def __init__(self, val):
        self.val = val

    def __call__(self, m):
        return []

    def __repr__(self):
        return 'Rem("' + str(self.val) + '")'


class LocalLabels:
    """Local sequential label for inside subr
    create a local labeler
    ll = LocalLabels()
    make a label - ll('test')
    reference the label - ll.test

    local labels that don't collide
    """

    def __init__(self):
        self._postfix = Postfix()
        self._names = {}

    def __call__(self, name):
        self._names[name] = name + self._postfix
        setattr(self, name, name + self._postfix)
        return L(name + self._postfix)

    def set(self, name):
        val = name + self._postfix
        self._names[name] = val
        setattr(self, name, val)
        return val

    def __getattr__(self, key):
        if key in self._names:
            return self._names[key]
        # for forward declarations
        self._names[key] = key + self._postfix
        setattr(self, key, key + self._postfix)
        return self._names[key]


class Window:
    """Allocatable register window
    this needs to be converted for the register allocator
    TODO : fix for the allocator
    """

    _REGS = [R0, R1, R2, R3, R4, R5, R6, R7]
    _size = 8

    def __init__(self, jumper=True):
        self._allocated = [False] * 8
        self._name = [""] * 8
        if jumper:
            # frame for subroutine calls R6 is fp , R7 is return
            self._allocated[6] = True
            self._name[6] = "fp"
            setattr(self, "fp", self._REGS[6])

            self._allocated[7] = True
            self._name[7] = "ret"
            setattr(self, "ret", self._REGS[7])

    def req(self, name):
        if type(name) == type(""):
            self._single(name)
        if type(name) == type([]):
            for i in name:
                self._single(i)

    def _single(self, name):
        for i in range(self._size):
            if self._allocated[i] == False:
                # free register
                self._allocated[i] = True
                self._name[i] = name
                if name not in self.__dict__:
                    setattr(self, name, self._REGS[i])
                    return
                else:
                    raise NameCollision(self)
        # no free registers
        # fail for now
        raise WindowFull(self)

    def __getitem__(self, key):
        if hasattr(self, key):
            return self.__dict__[key]

    # TODO spill and reuse registers


class MetaSub(type):
    subroutines = []
    """
    Meta Sub is a class for collecting all the routines together
    It also expands the useds subroutines for adding in the epilogue of the
    program
    """

    def __new__(cls, clsname, bases, attrs):
        newclass = super(MetaSub, cls).__new__(cls, clsname, bases, attrs)
        cls.register(newclass)  # here is your register function
        return newclass

    def register(cls):
        d = MetaSub.subroutines
        if cls.__qualname__ == "SubR":
            # Don't add root subclass
            return
        if cls not in d:
            d.append(cls())

    @classmethod
    def code(cls):
        li = MetaSub.subroutines
        # loop through and add sub-subroutines to the list
        # this will scan through the subs and add called subs
        # to the list
        c = []
        while True:
            old_c = c
            c = []
            for i in li:
                if i._called:
                    c.append(i.code())
            if len(old_c) == len(c):
                break
        log.info("Working subroutines")
        for i in li:
            if i._called:
                log.info("\t  - %s ", i.name)
        # TODO lib code vector
        return c


class SubR(metaclass=MetaSub):
    """
    Calling Standard
    R7 = return address (used by the child frame)
    R6 = frame pointer

    Call structure

    1. copy registers up into frame
    2. jump into subroutine
    3. shift window up
    4. run code
    5. shift window down
    6. return from jump
    7. copy data from upper frame

    """

    debug = True

    _called = False

    def __init__(self):
        self.w = Window()
        # return registers to upper window
        self._ret = False
        self._ret_target = []
        self._size = 1  # for later ( stack frames ) TODO
        self.setup()
        self._built = False
        # is it a lib function
        self._lib = False
        if not hasattr(self, "name"):
            self.name = type(self).__qualname__

        if hasattr(self, "params"):
            self.length = len(self.params)
            for i in self.params:
                self.w.req(i)
        else:
            self.length = 0
        if hasattr(self, "locals"):
            for i in self.locals:
                self.w.req(i)
        if hasattr(self, "ret"):
            self._ret_len = len(self.ret)
            self._ret = True
            for i in self.ret:
                # return registers can be existing registers
                if i not in self.w.__dict__:
                    self.w.req(i)
        if not self._built:
            self.build()
            self._built = True

    @classmethod
    def mark(cls):
        "include code if the subroutine has been called"
        cls._called = True

    def setup(self):
        # Override me.
        pass
        # log.warning("{} should have setup function".format(type(self).__qualname__))
        # raise FWError("Need to set up subroutine , params , locals and ret")

    def build(self):
        # build the objects and stuff
        # log.critical(self)
        # log.info("No Build me")
        pass

    def __call__(self, *args, **kwargs):
        # TODO this will need to be rewritten for the allocator
        if len(args) != self.length:
            raise ValueError(
                "Parameter count is should be '{}' in  {}".format(
                    self.params, self.name
                )
            )
        # load the parameters into the next frame up
        instr = []
        for i, j in enumerate(args):
            source = j
            target = self.w[self.params[i]].value
            if self.debug:
                instr += [Rem("Load " + self.params[i])]
            instr += [ST(source, self.w.fp, -self._size * 8 + target)]

        instr += [JAL(self.w.ret, self.name)]

        # This adds a code to copy registers down into the previous frame
        # if requested with a ret=[return,register] in the call
        if "ret" in kwargs:
            if self._ret:
                self._ret_target = []
                vals = kwargs["ret"]
                if type(vals) == type([]):
                    if len(vals) > self._ret_len:
                        raise ValueError("To many returns")
                    for i, j in enumerate(vals):
                        source = self.w[self.ret[i]]
                        instr += [Rem("Return " + self.ret[i])]
                        instr += [LD(j, self.w.fp, -self._size * 8 + source.value)]
                else:
                    source = vals
                    target = self.w[self.ret[0]].value
                    instr += [Rem("Return " + self.ret[0])]
                    instr += [LD(source, self.w.fp, -self._size * 8 + target)]

            else:
                raise ValueError("No return registers exist")

        if False:  # self.debug:
            "clean up the above frame"
            instr += [MOVI(self.w.ret, 0)]
            for i in range(8, 0, -1):
                instr += [ST(self.w.ret, self.w.fp, -i)]
        self.mark()
        return instr

    def instr(self):
        "empty code"
        return []

    def code(self):
        # TODO This needs to change for the allocator
        data = [L(self.name)]
        data += [L(self.name + "_start")]
        if self.__doc__ is not None:
            data.append(Rem(self.__doc__))
        if self.debug:
            data += [Rem(self.w._name[0:4])]
            data += [Rem(self.w._name[4:8])]
        data += [ADJW(-self._size * 8)]  # window shift up
        data += [LDW(self.w.fp, 0)]  # save window
        data += [Rem("--- ENTER ---")]
        data += [self.instr()]  # all it's instructions
        data += [Rem("--- EXIT  ---")]
        data += [ADJW(self._size * 8), JR(R7, 0)]  # shift window down
        data += [L(self.name + "_end")]
        return data
