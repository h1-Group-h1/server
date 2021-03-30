import paho.mqtt.client as mqtt
import json

client = mqtt.Client()


def on_connect(client, userdata, flags, rc):
    if rc != mqtt.MQTT_ERR_SUCCESS:
        print("ERROR: Failed to connect")
        exit(0)  # Need better solution
    client.subscribe('$SYS/#')


def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))
    device_id = msg.topic.split('/')
    payload = json.loads(msg.payload)
    if device_id[1] == 'sensor':
        # Sensor or remote
        pass
    elif device_id[1] == 'device':
        # Device
        pass


def operate_device(device_id, value):
    command = {"command": "operate", "payload": value}
    client.publish(device_id, json.dump(command))


client.on_connect = on_connect
client.on_message = on_message
client.connect("mqtt.eclipse.org")

client.loop_start()
