import multiprocessing
from concurrent.futures.thread import ThreadPoolExecutor
from threading import Thread

import paho.mqtt.client as mqtt
import crud
import main

def on_connect(client, userdata, flags, rc):
    print("MQTT client connected")
    client.subscribe("sensors/#")
    client.subscribe("remotes/#")
    # server/# --> Data from devices to server
    # devices/# --> Data from server to devices


def on_message(client, userdata, msg):
    if msg.topic.startswith("sensors") or msg.topic.startswith("remotes"):
        print(msg.topic)
        sn = int(msg.topic.split('/')[1])
        if msg.topic.startswith("sensors"):
            db = main.get_db()
            db_device = crud.get_device_by_sn(db, sn)
            db_rule = crud.get_rule(db, msg.payload)
            notify_device(sn, db_rule.value)
        elif msg.topic.startswith("remotes"):
            # Remote pressed - get
            # Payload: First 4 bytes = device sn, last one is new value
            raw = msg.payload.encode("utf-8")
            sn = int(raw[0:4])
            value = int(raw[4:5])
            notify_device(str(sn), (value >> 8).to_bytes(4, "little"))  # Arduino is little-endian
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
