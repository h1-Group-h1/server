import paho.mqtt.client as mqtt
from bitstring import BitStream, BitArray


def on_connect(client, userdata, flags, rc):
    print("MQTT test client connected")
    client.subscribe("server/123")
    client.subscribe("server/124")
    # Start tests
    print("Master tests starting")
    test_data = [
        ["devices/sensors/123", 102]
    ]

    for test in test_data:
        client.publish(test[0], str(test[1]))


def on_message(client, userdata, msg):
    print("Received from:", msg.topic, "    data:", msg.payload)


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("test.mosquitto.org")
print("Master tests starting")

client.loop_forever()
