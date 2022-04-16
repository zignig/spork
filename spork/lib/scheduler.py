" Scheduler and tasks"

from boneless.arch.opcode import Instr
from boneless.arch.opcode import *

from .stringer import Stringer
from .alloc import GAlloc

from ..firmware.base import *

from ..logger import logger

log = logger(__name__)

__done__ = False


class Scheduler(CodeObject):
    "Base Scheduler"

    def __init__(self):
        log.info("Base Scheduler")
        super().__init__()


class CreateTask(SubR):
    """
        Take an address to the task data
        1. Allocate Memory
        2. Save Heap pointer
        3. Save Window reference
    """

    def setup(self):
        self.param = ["pointer"]


class CreateScheduler(SubR):
    def setup(self):
        self.locals = ["pointer", "count", "hpointer"]
        self.param = ["count"]

    def instr(self):
        w = self.w
        self.globals.sched = 0
        self.globals.task_count = self.tasks
        self.stringer.start = "Starting"
        al = GAlloc()
        task_build = []
        for i in range(self.tasks):
            task_build.append(Rem("task %s" % i))
        return [
            Rem("Alloc count + 1 and return pointer"),
            Rem("Global alloc"),
            MOVI(w.count, self.tasks + 1),
            al(w.count, ret=[w.pointer]),
            self.globals.sched(w.hpointer),
            ST(w.pointer, w.hpointer, 0),
            task_build,
        ]


class FCFS(Scheduler):
    "First come first served"

    def __init__(self):
        super().__init__()
        self.tasks = []
        self.names = Stringer()

    def add_task(self, task):
        self.names.add(task.name, task.name)
        self.tasks.append(task)

    def setup(self):
        self.cs = CreateScheduler()
        # evil hack , attach to the class
        CreateScheduler.tasks = len(self.tasks)
        return [Rem("Setup the Scheduler"), self.cs()]

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
        return [0, 0, self.interval, self.size, 0, 0, 0, 0]


if __name__ == "__main__":
    print("Scheduler")
    s = FCFS()
