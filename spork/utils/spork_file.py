# handler for the spork file

import toml

from ..logger import logger

log = logger(__name__)


def load_spork(file_name):
    data = open(file_name).read()
    print(data)
    as_toml = toml.loads(data)
    the_spork = ASpork(as_toml)
    return the_spork


class ASpork:
    def __init__(self, attr):

        self.data = attr
        log.info("Spork file entries %s", attr)
        for i in attr:
            log.debug("{:s} -> {:s}".format(i, str(attr[i])))
            setattr(self, i, attr[i])

    def show(self):
        for i in self.data:
            print("{:15} : {:s}".format(i, str(self.data[i])))
