#!/usr/bin/python

import serial, time

port = "/dev/ttyUSB0"
baud = 115200
bl = serial.serial_for_url(port, baud, timeout=0.5, dsrdtr=False, do_not_open=True)
bl.dtr = 0
bl.rts = 0


def toggle(count):
    for i in range(count):
        print("toggle 0")
        time.sleep(0.1)
        bl.dtr = 1
        print("toggle 1")
        bl.dtr = 0
    bl.dtr = 1


bl.open()
toggle(2)  # bootloader
# toggle(4) # warm boot into image
bl.close()
time.sleep(0.5)
