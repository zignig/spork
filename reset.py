#!/usr/bin/python

import serial, time

bl = serial.Serial("/dev/ttyUSB0", 115200, timeout=0.5, dsrdtr=False)


def toggle(count):
    for i in range(count):
        print("toggle 0")
        time.sleep(0.1)
        bl.dtr = 1
        print("toggle 1")
        bl.dtr = 0
    bl.dtr = 1


toggle(2)  # bootloader
# toggle(4) # warm boot into image
bl.close()
time.sleep(0.5)
