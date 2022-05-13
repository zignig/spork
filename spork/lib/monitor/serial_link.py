#!/usr/bin/python -i
"""
    Primary serial link and encoder

    Manages packet transactions from the host side

"""


import serial
import struct
import time

from .defines import Commands, MAGIC


class MonitorError(Exception):
    pass


class Timeout(MonitorError):
    pass


class BadMagic(MonitorError):
    pass


class CRCError(MonitorError):
    pass


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


class MonInterface:
    def __init__(self, port="/dev/ttyUSB0", baud=115200):
        try:
            self._port = port
            self._baud = baud
            self._ser = None
            self._connected = False

            # self.connect()
        except:
            print("Serial Port Fail")

    def connect(self):
        self._connected = True
        self._ser = serial.serial_for_url(
            self._port, self._baud, timeout=0.1, dsrdtr=False
        )
        self._ser.dtr = 0
        # clear out the buffers
        self._ser.reset_input_buffer()
        self._ser.reset_output_buffer()
        try:
            self.ping()
        except:
            print("no response")
            return
        print("monitor connected")

    def _ser_write(self, data):
        if not self._connected:
            self.connect()
        sent = 0
        while sent != len(data):
            sent += self._ser.write(data[sent:])

    def _ser_read(self, length):
        if not self._connected:
            self.connect()
        read = b""
        while length > 0:
            new = self._ser.read(length)
            if len(new) == 0:
                raise Timeout("read timeout")
            read += new
            length -= len(new)
        return read

    def _packet_write(self, command, param1, param2):
        crc = _crc((command, param1, param2))
        packet = (MAGIC, command, param1, param2, crc)
        # print("packet")
        # print(packet)
        encoded = struct.pack(">{}H".format(5), *packet)
        # print(encoded)
        self._ser_write(encoded)

    def _packet_read(self):
        s = self._ser_read(10)
        # print(s)
        val = struct.unpack(">{}H".format(5), s)
        # print(val)
        return val

    def ping(self):
        start = time.time()
        self.pack(Commands.hello)
        finish = time.time()
        print(finish - start)
        return True

    def data_read(self, length):
        "read words of length + crc"
        data = self._ser_read(length * 2 + 2)
        value = struct.unpack(">{}H".format(length + 1), data)
        crc = value[-1]
        data = value[:-1]
        crc_data = _crc(data)
        if crc_data != crc:
            raise CRCError()
        return data

    def data_write(self, data):
        crc = _crc(data)
        l = len(data)
        data = data + (crc,)
        print(data)
        value = struct.pack(">{}H".format(l + 1), *data)
        self._ser_write(value)

    def pack(self, val, p1=0, p2=0):
        self._packet_write(val, p1, p2)
        data = self._packet_read()
        # check the header
        if data[0] != MAGIC:
            raise BadMagic()
        # check the crc
        crc = _crc(data[1:4])
        if crc != data[4]:
            raise CRCError(data)
        return (Commands(data[1]), data[2], data[3])
