import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc):
	print("Connected with code", rc)

client = mqtt.Client()
client.on_connect = on_connect
client.connect("35.202.76.0", port=1883)
