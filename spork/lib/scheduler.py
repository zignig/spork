" Scheduler and tasks"

from boneless.arch.opcode import Instr
from boneless.arch.opcode import *

from .stringer import Stringer
from .alloc import GAlloc

from ..firmware.base import *

from ..logger import logger

log = logger(__name__)


class Scheduler(CodeObject):
    "Base Scheduler"

    def __init__(self):
        log.info("Base Scheduler")
        super().__init__()


class FCFS(Scheduler):
    "First come first served"

    class CreateScheduler(SubR):
        def setup(self):
            self.locals = ["pointer", "count", "hpointer"]
            self.param = ["count"]

        def instr(self):
            w = self.w
            self.globals.sched = 0
            al = GAlloc()
            return [
                Rem("Alloc count + 1 and return pointer"),
                Rem("Global alloc"),
                self.globals.heap_pointer(w.hpointer),
                ADDI(w.count, w.count, 1),
                al(w.count, ret=[w.pointer]),
            ]

    def __init__(self):
        super().__init__()
        self.tasks = []
        self.names = Stringer()
        self.names.all()

    def add_task(self, task):
        self.names.add(task.name, task.name)
        self.tasks.append(task)

    def setup(self):
        cs = self.CreateScheduler()

        return [Rem("Setup the Scheduler"), cs()]

    def code(self):
        t = []
        for i in self.tasks:
            t.append(i.code())
        return [Rem("tasks"), L("tasks"), t]


class Task(CodeObject):
    def __init__(self, name="none", size=16, interval=512):
        self.name = name
        self.interval = interval
        self.size = size

    def code(self):
        return 8 * [0]


if __name__ == "__main__":
    print("Scheduler")
    s = FCFS()
