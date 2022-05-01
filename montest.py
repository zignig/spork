#!/usr/bin/python -i
" monitor python console interface"

from spork.lib.monitor.serial_link import MonInterface
from spork.lib.monitor.mon_firm import MonitorFirm
from rich import print
import sys

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--firmware", action="store_true")
    parser.add_argument("-l", "--list", action="store_true")

    args = parser.parse_args()
    if args.list or args.firmware:
        import fwtest

        spork = fwtest.build(MonitorFirm, detail=False)
        if args.list:
            print(spork.fw.code())
        else:
            if args.firmware:
                from spork.upload import Uploader

                up = Uploader()
                up.upload(spork, console=False)

    m = MonInterface()
