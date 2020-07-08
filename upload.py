" Serial interface for uploading boneless firmware"

from itertools import zip_longest


def grouper(iterable, n, fillvalue=None):
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)


class Uploader:
    def __init__(self, port="/dev/ttyUSB0", baud=115200):
        pass

    def upload(self, firmware):
        self.hex_blob = firmware.hex_blob
        for i in grouper(self.hex_blob, 4):
            data = "".join(i)
            print(data)
