import multiprocessing
from concurrent.futures.thread import ThreadPoolExecutor
from threading import Thread

import paho.mqtt.client as mqtt
import crud
import main

# Idea - have seperate topic for each action

def on_connect(client, userdata, flags, rc):
    print("MQTT client connected")
    client.subscribe("devices/sensors/#")
    client.subscribe("devices/remotes/#")
    # server/# --> Data from devices to server
    # devices/# --> Data from server to devices


def on_message(client, userdata, msg):
    if msg.topic.startswith("devices/sensors") or msg.topic.startswith("devices/remotes"):
        print(msg.topic)
        sn = int(msg.topic.split('/')[1])
        if msg.topic.startswith("devices/sensors"):
            db = main.get_db()
            db_device = crud.get_device_by_sn(db, sn)
            db_rule = crud.get_rule(db, msg.payload)
            notify_device(sn, db_rule.value)
        elif msg.topic.startswith("devices/remotes"):
            # Remote pressed - get
            # Payload: First byte = command (0x1 for set device, 0x0 for
            # get devices), next 4 bytes = device sn, last one is new value
            raw = msg.payload.encode("utf-8")
            command = int(raw[0])
            sn = int(raw[1:5])
            value = int(raw[5])
            if command = 0x1:
                notify_device(str(sn), (value >> 8).to_bytes(4, "little"))  # Arduino is little-endian
            else:
                # Get devices and send

            pass


# Communicate via sn
def notify_device(device: str, payload: bytes):
    global client
    client.publish("server/" + device, payload)


client = mqtt.Client()


def mqtt_main():
    global client
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect("test.mosquitto.org")
    print("Client ready for action")
    client.loop_start()
