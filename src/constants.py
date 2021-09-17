# Sets debug mode
import os
debug = True
if os.getenv("DEBUG_MODE") == "False":
    debug = False
enable_master_tests = True

version = os.getenv("VER")
error = 1
warning = 2
info = 3

DEVICE_SENSOR = "sensor"
DEVICE_DEVICE = "device"

KEYFILE_PATH = "/var/royal-automation/access_keys/key.txt"
DEVICEFILE_PATH = "/etc/mosquitto/passwd/ra-pwfile.txt" # TODO: encrypt