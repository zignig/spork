"""
    Command ID for the monitor
"""

# defines for the monitor
from enum import IntEnum


MAGIC = 0x6676
FIRMWARE_VERSION = 0x0003
GATEWARE_VERSION = 0x0006


class MemoryBlock:
    def __init__(self, address, size):
        self.address = address
        self.size = size
        self.data = [0] * int(size)


class Commands(IntEnum):
    hello = 1
    write_data = 2
    read_data = 3
    version = 4
    jump = 5
    alloc = 6
    free = 7
    write_external = 8
    # read_external = 8
    # load_code = 9
    # read_code = 10
    # delete_code = 11
    # list_code = 12
    # watch = 13
    # reset = 14
    # core_dump = 15
    # unwind_stack = 16
    # and more

    # OK
    ok = 100
    # ERROR
    error = 101
    crc_error = 102
    no_command = 103
