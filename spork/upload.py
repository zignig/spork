" Serial interface for uploading boneless firmware"


from itertools import zip_longest
from serial.tools.miniterm import Miniterm
import serial
import time

from rich import print
from .logger import logger

log = logger(__name__)


# CRC
# implementation taken from crcany
# lifted from https://github.com/tpwrules/ice_panel/
def _crc(words):
    crc = 0
    for word in words:
        crc ^= word
        for bi in range(16):
            if crc & 1:
                crc = (crc >> 1) ^ 0x8408
            else:
                crc >>= 1
    return crc


def grouper(iterable, n, fillvalue=None):
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)


class Uploader:
    def __init__(self, port="/dev/ttyUSB0", baud=115200):
        self.port = port
        self.baud = baud
        self.ser = serial.serial_for_url(
            port, baud, timeout=0.5, dsrdtr=False, do_not_open=True
        )
        # self.ser.dtr = 0

    def toggle(self, count):
        # toggles the DTR pin, there is a internal reset device
        for i in range(count):
            time.sleep(0.1)
            self.ser.dtr = 1
            # print("toggle 1")
            self.ser.dtr = 0
        # self.ser.dtr = 1
        time.sleep(0.8)

    def upload(self, firmware, console=True, reset=True):
        import argparse

        parser = argparse.ArgumentParser()
        parser.add_argument("-l", "--list", action="store_true")
        parser.add_argument("-v", "--verbose", action="store_true")

        args = parser.parse_args()
        if args.list:
            log.info("Listing information")
            print(firmware.fw.reg.show())
            print(firmware.fw.code())
            print(firmware.hex_blob)
        else:
            if reset:
                log.info("Reset device")
                self.ser.open()
                # warmboot
                self.toggle(4)
                self.hex_blob = firmware.hex_blob
                # self.ser.readall()  # clear out the buffer
                # self.ser.write(4)
                # wait for the pll to settle
                time.sleep(0.3)
                counter = 0
                log.info("Upload Firmware")
                for i in grouper(self.hex_blob, 4):
                    data = "".join(i).encode()
                    # print(data)
                    # counter += 1
                    # if counter % 4 == 0:
                    #    print('.',end="")
                    self.ser.write(data)
                # a = self.ser.readall()
                # print(a)
            if console:
                log.info("Create Terminal")
                term = Miniterm(self.ser)
                term.set_rx_encoding("utf-8")
                term.set_tx_encoding("utf-8")
                term.exit_character = "\x1d"
                log.info("Attach Terminal")
                term.start()
                term.join(True)
