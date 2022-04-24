# The serial link and encoder

#

# Connect
# Send
# Recieve
# Check
from .commands import CL


class Interlink:
    "Handles serial connections"

    def __init__(self, device, baud):
        self.port = None
        self.device = device
        self.baud = baud

    def _connect(self):
        pass

    def _send(self):
        pass

    def _recive(self):
        pass

    def _check(self):
        pass
