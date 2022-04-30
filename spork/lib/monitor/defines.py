# defines for the monitor
from enum import IntEnum


MAGIC = 0x6676


class Commands(IntEnum):
    hello = 1
    write_data = 2
    read_data = 3
    jump = 4
    free = 5
    version = 6
    write_external = 7
    read_external = 8
    load_code = 9
    read_code = 10
    delete_code = 11
    list_code = 12
    watch = 13
    reset = 14
    core_dump = 15
    unwind_stack = 16
    # and more

    # OK
    ok = 100
    # ERROR
    error = 101
    crc_error = 102
    no_command = 103
