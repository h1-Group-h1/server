# Sets debug mode
import os
debug = True
if os.getenv("DEBUG_MODE") == "False":
    debug = False
enable_master_tests = True
version = "1.2.1"
error = 1
warning = 2
info = 3

DEVICE_SENSOR = "sensor"
DEVICE_DEVICE = "device"
