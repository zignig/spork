import asyncio
import serial_asyncio


class Ser(asyncio.Protocol):
    def connection_made(self, transport):
        """Store the serial transport and prepare to receive data.
        """
        self.transport = transport
        self.buf = bytes()
        self.msgs_recvd = 0
        print("Reader connection created")
        asyncio.ensure_future(self.send())
        print("Writer.send() scheduled")

    def data_received(self, data):
        print("rec", data)

    def connection_lost(self, exc):
        print("Reader closed")

    async def send(self):
        await asyncio.sleep(5)
        """Send four newline-terminated messages, one byte at a time.
        """
        message = b"foo\nbar\nbaz\nqux\n"
        for i in range(1000):
            # await asyncio.sleep(0.02)
            print(i, "send", message)
            self.transport.serial.write(bytes(message))


loop = asyncio.get_event_loop()
t = serial_asyncio.create_serial_connection(
    loop, Ser, "/dev/ttyUSB0", baudrate=115200, timeout=0.4
)
asyncio.ensure_future(t)
loop.call_later(10, loop.stop)
loop.run_forever()
print("Done")
