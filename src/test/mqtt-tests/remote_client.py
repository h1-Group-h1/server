import paho.mqtt.client as mqtt

SN = 3456

def on_connect(client, userdata, flags, rc):
    print("MQTT client connected")
    client.subscribe("server/remotes/{0}".format(SN))


def on_message(client, userdata, msg):
    print("Message from:", msg.topic, "reads", msg.payload)
    house_id = int(msg.payload[0:6])
    print("new house:", house_id)
    # Notify to get devices - devices/remotes/get_house_info




client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("test.mosquitto.org")
print("Client ready for action")
client.loop_start()

while True:
    # Test server