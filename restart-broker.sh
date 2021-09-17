KEYFILE_PATH="/tmp/royal-automation/access_keys/key.txt"
DEVICEFILE_PATH="/var/royal-automation/devices.txt"

# Todo: write
service mosquitto stop

# Create password
mosquitto_passwd -U /etc/mosquitto/passwd/ra-pwfile.txt


service mosquitto start
service mosquitto enable
