import paho.mqtt.client as mqtt
import json
import time



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
  "value_template": "{{ value_json." + entity_id + " }}"
}

discovery_topic = f"homeassistant/sensor/{device_id}/{entity_id}/config"
infot = mqttc.publish(discovery_topic, json.dumps(msg), qos=2)
infot.wait_for_publish()

try:
    while True:
        val = 230

        data = {
            "l1_voltage": val,
            "l2_voltage": val,
            "l3_voltage": val,
            "total_active_energy": 0.04,
        }

        infot = mqttc.publish(f"emon/{device_id}", json.dumps(data), qos=2)
        infot.wait_for_publish()
        print("publish")
        time.sleep(10)
except KeyboardInterrupt:
    pass


