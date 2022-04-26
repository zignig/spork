#!/usr/bin/python
" monitor test interface"

"""
>>> t
b'Z\x04\x00\x01\x00\x00\x00\x00\x00\x00'
>>> r  = struct.unpack('>{}H'.format(7),t)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
struct.error: unpack requires a buffer of 14 bytes
>>> r  = struct.unpack('>{}H'.format(5),t)
"""

import serial


class Mon:
    def __init__(self, port="/dev/ttyUSB0", baud=115200):
        try:
            self.port = port
            self.baud = baud
            self.ser = serial.serial_for_url(port, baud, timeout=0.5, dsrdtr=False)
            self.ser.dtr = 0
        except:
            print("fail")


m = Mon()
