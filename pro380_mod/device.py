
import struct
import socket
import logging
from dataclasses import dataclass
from pymodbus.utilities import computeCRC, checkCRC
from typing import Callable,Any
from functools import partial

import paho.mqtt.client as mqtt
import json
import time



log = logging.getLogger()
logging.basicConfig(level=logging.INFO)


def to_hex(b: bytes):
    return ' '.join(format(x, "02x") for x in b)


@dataclass
class Command():
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
    return int.from_bytes(data, byteorder='big')




SERIAL_NUMBER =             Command(0x4000, 4, hex_to_str)
METER_CODE =                Command(0x4002, 2, hex_to_str)
METER_ID =                  Command(0x4003, 2, hex_to_str)
BAUD_RATE =                 Command(0x4004, 2, into_int)
PROTOCOL_VERSION =          Command(0x4005, 4, partial(single_value,">f"))
SOFTWARE_VERSION =          Command(0x4007, 4, partial(single_value,">f"))
HARDWARE_VERSION =          Command(0x4009, 4, partial(single_value,">f"))
METER_AMPS =                Command(0x400B, 2, into_int)
CT_RATE =                   Command(0x400C, 2, into_int)
S0_OUTPUT_RATE =            Command(0x400D, 4, partial(single_value,">f"))
COMBINATION_CODE =          Command(0x400F, 2, into_int)
LCD_CYCLE_TIMW =            Command(0x4010, 2, hex_to_str)
PARITY_SETTING =            Command(0x4011, 2, into_int)
CURRENT_DIRECTION =         Command(0x4012, 6, str)



GRID_FREQUENCY =            Command(0x5008, 4, partial(single_value,">f"))
TOTAL_ACTIVE_POWER =        Command(0x5012, 4, partial(single_value,">f"))
TOTAL_ACTIVE_ENERGY =       Command(0x6000, 4, partial(single_value,">f"))
RESETTABLE_DAY_COUNTER =    Command(0x6049, 4, partial(single_value,">f"))
ALL_VOLTAGE =               Command(0x5002, 12, partial(multiple_values,">fff"))
ALL_CURRENT =               Command(0x500C, 12, partial(multiple_values,">fff"))

class Device():

    def __init__(self, host: str, dev_id:int = 1):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, 502))
        self.dev_id = dev_id

    def close(self):
        self.sock.close()

    def read(self, register:int, size:int) -> bytes:
        msg = self.dev_id.to_bytes(1, byteorder="big") + b"\x03" \
              + register.to_bytes(2, byteorder="big") \
              + (size // 2).to_bytes(2, byteorder="big")
        msg = msg + computeCRC(msg).to_bytes(2, byteorder="big")
        log.debug(" send: " + to_hex(msg))
        self.sock.send(msg)
        data = self.sock.recv(size*2 + 3 + 2)
        log.debug(" recv: " + to_hex(data))

        if not checkCRC(data[:-2], int.from_bytes(data[-2:], byteorder="big")):
            raise Exception("Failed CRC check")

        return data[3:-2]

    def cmd(self, cmd: Command) -> Any:
        data = self.read(cmd.register, cmd.size)
        return cmd.convert(data)


mqttc = mqtt.Client()
mqttc.connect("192.168.88.28", 1883, 60)
mqttc.loop_start()

device_id = "pro380_1"

device_dict = {
    "identifiers": device_id,
    "name": "Inepro PRO380",
    "manufacturer": "Inepro Metering",
    "model": "Inepro PRO380-Mod 3-Phase Energy Monitor"
}


entity_id = "l1_voltage"
entity_name = "L1_Voltage"
entity_unit = "V"
entity_class = "Voltage"
msg = {
  "stat_t": "emon/" + device_id,
  "device": device_dict,
  "uniq_id": device_id + "_" + entity_id,
  "name": entity_name,
  "unit_of_meas": entity_unit,
  "device_class": entity_class,
  "value_template": "{{ value_json." + entity_id + " }}"
}

discovery_topic = f"homeassistant/sensor/{device_id}/{entity_id}/config"
infot = mqttc.publish(discovery_topic, json.dumps(msg), qos=2)
infot.wait_for_publish()

entity_id = "l2_voltage"
entity_name = "L2_Voltage"
entity_unit = "V"
entity_class = "Voltage"
msg = {
  "stat_t": "emon/" + device_id,
  "device": device_dict,
  "uniq_id": device_id + "_" + entity_id,
  "name": entity_name,
  "unit_of_meas": entity_unit,
  "device_class": entity_class,
  "value_template": "{{ value_json." + entity_id + " }}"
}

discovery_topic = f"homeassistant/sensor/{device_id}/{entity_id}/config"
infot = mqttc.publish(discovery_topic, json.dumps(msg), qos=2)
infot.wait_for_publish()


entity_id = "l3_voltage"
entity_name = "L3_Voltage"
entity_unit = "V"
entity_class = "Voltage"
msg = {
  "stat_t": "emon/" + device_id,
  "device": device_dict,
  "uniq_id": device_id + "_" + entity_id,
  "name": entity_name,
  "unit_of_meas": entity_unit,
  "device_class": entity_class,
  "value_template": "{{ value_json." + entity_id + " }}"
}

discovery_topic = f"homeassistant/sensor/{device_id}/{entity_id}/config"
infot = mqttc.publish(discovery_topic, json.dumps(msg), qos=2)
infot.wait_for_publish()

entity_id = "l1_current"
entity_name = "L1_Current"
entity_unit = "A"
entity_class = "Current"
msg = {
  "stat_t": "emon/" + device_id,
  "device": device_dict,
  "uniq_id": device_id + "_" + entity_id,
  "name": entity_name,
  "unit_of_meas": entity_unit,
  "device_class": entity_class,
  "value_template": "{{ value_json." + entity_id + " }}"
}

discovery_topic = f"homeassistant/sensor/{device_id}/{entity_id}/config"
infot = mqttc.publish(discovery_topic, json.dumps(msg), qos=2)
infot.wait_for_publish()


entity_id = "l2_current"
entity_name = "L2_Current"
entity_unit = "A"
entity_class = "Current"
msg = {
  "stat_t": "emon/" + device_id,
  "device": device_dict,
  "uniq_id": device_id + "_" + entity_id,
  "name": entity_name,
  "unit_of_meas": entity_unit,
  "device_class": entity_class,
  "value_template": "{{ value_json." + entity_id + " }}"
}


discovery_topic = f"homeassistant/sensor/{device_id}/{entity_id}/config"
infot = mqttc.publish(discovery_topic, json.dumps(msg), qos=2)
infot.wait_for_publish()

entity_id = "grid_frequency"
entity_name = "Grid Frequency"
entity_unit = "Hz"
entity_class = "frequency"
msg = {
  "stat_t": "emon/" + device_id,
  "device": device_dict,
  "uniq_id": device_id + "_" + entity_id,
  "name": entity_name,
  "unit_of_meas": entity_unit,
  "device_class": entity_class,
  "value_template": "{{ value_json." + entity_id + " }}"
}


discovery_topic = f"homeassistant/sensor/{device_id}/{entity_id}/config"
infot = mqttc.publish(discovery_topic, json.dumps(msg), qos=2)
infot.wait_for_publish()

entity_id = "l3_current"
entity_name = "L3_Current"
entity_unit = "A"
entity_class = "Current"
msg = {
  "stat_t": "emon/" + device_id,
  "device": device_dict,
  "uniq_id": device_id + "_" + entity_id,
  "name": entity_name,
  "unit_of_meas": entity_unit,
  "device_class": entity_class,
  "value_template": "{{ value_json." + entity_id + " }}"
}

discovery_topic = f"homeassistant/sensor/{device_id}/{entity_id}/config"
infot = mqttc.publish(discovery_topic, json.dumps(msg), qos=2)
infot.wait_for_publish()

entity_id = "total_active_energy"
entity_name = "Total Active Energy"
entity_unit = "kWh"
entity_class = "energy"
msg = {
  "stat_t": "emon/" + device_id,
  "device": device_dict,
  "uniq_id": device_id + "_" + entity_id,
  "name": entity_name,
  "unit_of_meas": entity_unit,
  "device_class": entity_class,
  "enabled_by_default": "true",
  "state_class": "total_increasing",
  "value_template": "{{ value_json." + entity_id + " }}"
}

discovery_topic = f"homeassistant/sensor/{device_id}/{entity_id}/config"
infot = mqttc.publish(discovery_topic, json.dumps(msg), qos=2)
infot.wait_for_publish()


dev = Device("192.168.88.22")
try:
    while True:
        val = 230

        voltage = dev.cmd(ALL_VOLTAGE)
        current = dev.cmd(ALL_CURRENT)

        data = {
            "l1_voltage": round(voltage[0], 2),
            "l2_voltage": round(voltage[1], 2),
            "l3_voltage": round(voltage[2], 2),
            "l1_current": round(current[0], 4),
            "l2_current": round(current[1], 4),
            "l3_current": round(current[2], 4),
            "grid_frequency": round(dev.cmd(GRID_FREQUENCY), 4),
            "total_active_energy": round(dev.cmd(TOTAL_ACTIVE_ENERGY), 4),
        }

        infot = mqttc.publish(f"emon/{device_id}", json.dumps(data), qos=2)
        infot.wait_for_publish()
        print("publish")
        time.sleep(30)
except KeyboardInterrupt:
    pass



# try:
#     serial = "{}".format(dev.cmd(SERIAL_NUMBER)))
#     device = "pro380_" + serial
#
#
#
#
#     print("meter code: {}".format(dev.cmd(METER_CODE)))
#     print("meter id: {}".format(dev.cmd(METER_ID)))
#     print("baud rate: {}".format(dev.cmd(BAUD_RATE)))
#
#     print("protocol version: {:0.2f}".format(dev.cmd(PROTOCOL_VERSION)))
#     print("software version: {:0.2f}".format(dev.cmd(SOFTWARE_VERSION)))
#     print("hardware version: {:0.2f}".format(dev.cmd(HARDWARE_VERSION)))
#     print("resettable day counter: {:0.4f}".format(dev.cmd(RESETTABLE_DAY_COUNTER)))
#     print("current direction {}".format(dev.cmd(CURRENT_DIRECTION)))
#
#
#     while True:
#         print("{:0.6f} kW".format(dev.cmd(TOTAL_ACTIVE_POWER)))
# except KeyboardInterrupt:
#     pass
# finally:
#     dev.close()


