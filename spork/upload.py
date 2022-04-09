" Serial interface for uploading boneless firmware"

from itertools import zip_longest
from pdb import _rstr
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
        try:
            from serial.tools.miniterm import Miniterm

            self.port = port
            self.baud = baud
            self.ser = serial.serial_for_url(
                port, baud, timeout=0.5, dsrdtr=False, do_not_open=True
            )
            self.ser.dtr = 0
        except:
            log.critical("No serial library")

    def toggle(self, count):
        # toggles the DTR pin, there is a internal reset device
        for i in range(count):
            time.sleep(0.2)
            self.ser.dtr = 1
            # print("toggle 1")
            self.ser.dtr = 0
        # self.ser.dtr = 1
        time.sleep(0.8)

    def upload(self, firmware, console=True, reset=True):
        import argparse
        from serial.tools.miniterm import Miniterm

        parser = argparse.ArgumentParser()
        parser.add_argument("-l", "--list", action="store_true")
        parser.add_argument("-v", "--verbose", action="store_true")

        args = parser.parse_args()
        if args.list:
            log.info("Listing information")
            # print(firmware.fw.reg.show())
            print(firmware.fw.code())
            print(firmware.hex_blob)
        else:
            if reset:
                log.info("Reset device")
                self.ser.open()
                # warmboot
                self.toggle(4)
                self.hex_blob = firmware.hex_blob
                time.sleep(0.5)
                counter = 0
                log.info("Upload Firmware")
                lines = self.hex_blob.split()
                r = len(lines[1])  # length after the header
                for i in lines:
                    # print(">> "+i)
                    self.ser.write(i.encode())
                    # a = self.ser.read(r)
                    # print("<< "+a.decode())
                    # print()
                # for i in grouper(self.hex_blob, 4):
                # data = "".join(i).encode()
                # counter += 1
                # print(counter,data,end='')
                # if counter % 4 == 0:
                #    print('.',end="")
                # self.ser.write(data)
                # if counter % 16 == 0:
                #    time.sleep(0.05)
                # time.sleep(0.01)

            if console:
                log.info("Create Terminal")
                term = Miniterm(self.ser)
                term.set_rx_encoding("utf-8")
                term.set_tx_encoding("utf-8")
                term.exit_character = "\x1d"
                log.info("Attach Terminal")
                term.start()
                term.join(True)
