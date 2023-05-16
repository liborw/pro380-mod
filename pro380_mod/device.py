
import struct
import socket
import logging
from pymodbus.utilities import computeCRC, checkCRC


log = logging.getLogger()
logging.basicConfig(level=logging.INFO)


def to_hex(b: bytes):
    return ' '.join(format(x, "02x") for x in b)


class Device():

    def __init__(self, host: str, dev_id:int = 1):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, 502))
        self.dev_id = dev_id

    def close(self):
        self.sock.close()

    def read(self, register:int, size:int) -> bytes:
        msg = self.dev_id.to_bytes(1) + b"\x03" + register.to_bytes(2) + size.to_bytes(2)
        msg = msg + computeCRC(msg).to_bytes(2)
        log.debug(" send: " + to_hex(msg))
        self.sock.send(msg)
        data = self.sock.recv(size*2 + 3 + 2)
        log.debug(" recv: " + to_hex(data))

        if not checkCRC(data[:-2], int.from_bytes(data[-2:])):
            raise Exception("Failed CRC check")

        return data[3:-2]

    def read_grid_frequency(self) -> float:
        data = self.read(0x2020, 2)
        return struct.unpack(">f", data)[0]

    def read_voltage(self) -> list[float]:
        data = self.read(0x2008, 6)
        return struct.unpack(">fff", data)

    def read_current(self) -> list[float]:
        data = self.read(0x2068, 6)
        return struct.unpack(">fff", data)

    def read_total_active_energy(self) -> float:
        data = self.read(0x2080, 2)
        return struct.unpack(">f", data)[0]




dev = Device("192.168.88.22")

dev.read(0x1010, 1)
print("grid frequency: {} Hz".format(dev.read_grid_frequency()))
print("voltage: {} V".format(dev.read_voltage()))
print("current: {} A".format(dev.read_current()))

try:
    while True:
        print("{} kWh".format(dev.read_total_active_energy()))
except KeyboardInterrupt:
    pass
finally:
    dev.close()


