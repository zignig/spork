" Serial interface for uploading boneless firmware"


from itertools import zip_longest
from serial.tools import miniterm
import serial
import time

from rich import print


def grouper(iterable, n, fillvalue=None):
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)


class Uploader:
    def __init__(self, port="/dev/ttyUSB0", baud=115200):
        self.port = port
        self.baud = baud
        self.ser = serial.Serial(port, baud, timeout=0.5, dsrdtr=False)

    def toggle(self, count):
        # toggles the DTR pin, there is a internal reset device
        for i in range(count):
            # print("toggle 0")
            time.sleep(0.05)
            self.ser.dtr = 1
            # print("toggle 1")
            self.ser.dtr = 0
        self.ser.dtr = 1
        time.sleep(0.5)

    def upload(self, firmware, console=True):
        import argparse

        parser = argparse.ArgumentParser()
        parser.add_argument("-l", "--list", action="store_true")
        parser.add_argument("-v", "--verbose", action="store_true")

        args = parser.parse_args()
        if args.list:
            print(firmware.fw.code())
        else:
            self.toggle(4)
            self.hex_blob = firmware.hex_blob
            self.ser.readall()  # clear out the buffer
            for i in grouper(self.hex_blob, 4):
                data = "".join(i).encode()
                self.ser.write(data)
            if console:
                miniterm.main(self.port, self.baud)
