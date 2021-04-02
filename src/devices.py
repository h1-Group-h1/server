import multiprocessing
from concurrent.futures.thread import ThreadPoolExecutor
from threading import Thread

import paho.mqtt.client as mqtt


def on_connect(client, userdata, flags, rc):
    print("MQTT client connected")
    client.subscribe("server/#")
    # server/# --> Data from devices to server
    # devices/# --> Data from server to devices


def on_message(client, userdata, msg):
    print("Message from", msg.topic, ":", msg.payload)


def notify_device(device: str, payload: str):
    global client
    client.publish("devices/" + device, payload)


client = mqtt.Client()

def mqtt_main():
    global client
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect("test.mosquitto.org")
    print("Client ready for action")
    client.loop_start()
