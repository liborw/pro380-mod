
import struct
import socket
import logging
from dataclasses import dataclass
from pymodbus.utilities import computeCRC, checkCRC
from typing import Callable,Any
from functools import partial



log = logging.getLogger()
logging.basicConfig(level=logging.INFO)


def to_hex(b: bytes):
    return ' '.join(format(x, "02x") for x in b)


@dataclass
class Command():
    command: int
    register: int
    size: int
    convert: Callable[[bytes], Any]

def hex_to_str(data:bytes) -> str:
    return "0x" + ''.join(format(x, "02x") for x in data)


def single_value(fmt: str, data: bytes) -> Any:
    return struct.unpack(fmt, data)[0]


def multiple_values(fmt: str, data: bytes) -> Any:
    return struct.unpack(fmt, data)


def into_int(data: bytes) -> int:
    int.from_bytes(data, byteorder='big')


SERIAL_NUMBER = Command(0x03, 0x1000, 4, hex_to_str)
METER_CODE = Command(0x03, 0x1010, 2, hex_to_str)
METER_ID = Command(0x03, 0x1018, 2, hex_to_str)
BAUD_RATE = Command(0x03, 0x1020, 2, into_int)
PROTOCOL_VERSION = Command(0x03, 0x1050, 4, single_value(">f"))
SOFTWARE_VERSION = Command(0x03, 0x1054, 4, single_value(">f"))
HARDWARE_VERSION = Command(0x03, 0x1058, 4, single_value(">f"))
METER_AMPS = Command(0x03, 0x1060, 2, into_int)
CT_RATE = Command(0x03, 0x1062, 2, into_int)

TOTAL_ACTIVE_POWER = Command(0x03, 0x2080, 4, single_value(">f"))


class Device():

    def __init__(self, host: str, dev_id:int = 1):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, 502))
        self.dev_id = dev_id

    def close(self):
        self.sock.close()

    def read(self, register:int, size:int) -> bytes:
        msg = self.dev_id.to_bytes(1) + b"\x03" \
              + register.to_bytes(2) \
              + (size / 2).to_bytes(2)
        msg = msg + computeCRC(msg).to_bytes(2)
        log.debug(" send: " + to_hex(msg))
        self.sock.send(msg)
        data = self.sock.recv(size*2 + 3 + 2)
        log.debug(" recv: " + to_hex(data))

        if not checkCRC(data[:-2], int.from_bytes(data[-2:])):
            raise Exception("Failed CRC check")

        return data[3:-2]

    def cmd(self, cmd: Command) -> Any:
        data = self.read(cmd.register, cmd.size)
        return cmd.convert(data)









dev = Device("192.168.88.22")

print("serial number: {} Hz".format(dev.cmd(SERIAL_NUMBER)))
print("meter code: {}".format(dev.cmd(METER_CODE)))


try:
    while True:
        print("{} kWh".format(dev.cmd(TOTAL_ACTIVE_POWER)))
except KeyboardInterrupt:
    pass
finally:
    dev.close()


