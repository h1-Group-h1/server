from types import TracebackType
import requests
from requests.auth import HTTPBasicAuth
import traceback
from termcolor import colored
import sys

passes: int = 0
fails: int = 0
n_a: int = 0

BASE_URL = "https://com-ra-api.co.uk/"
if len(sys.argv) > 1:
    BASE_URL = sys.argv[1]

USERNAME = "test_sanity"
PASSWORD = "p"

def do_test(method, endpoint, expected_response=None, data=None):
    r = None
    if method == "POST":
        r = requests.post(BASE_URL + endpoint, auth=HTTPBasicAuth(USERNAME, PASSWORD), json=data)
    elif method == "DELETE":
        r = requests.delete(BASE_URL + endpoint, auth=HTTPBasicAuth(USERNAME, PASSWORD))
    elif method == "GET":
        r = requests.get(BASE_URL + endpoint, auth=HTTPBasicAuth(USERNAME, PASSWORD))
    if expected_response == None:
        print("Response for test", endpoint, "is:\n", r.json())
        global n_a
        n_a += 1
        return r.json()
    else:
        try:
            failed = False
            for key in expected_response:
                if r.json()[key] != expected_response[key]:
                    if not failed:
                        print("\033[91m {}\033[00m" .format("FAILED: "), end="")
                        print(BASE_URL+ endpoint)
                        failed = True
                        print("Expected response:", expected_response)
                        print("Got response:", r.json())
                        print("Status code:", r.status_code)
                        global fails
                        fails += 1
                        return r.json()

            print("\033[92m {}\033[00m" .format("Passed: "), end="")
            print(BASE_URL+ endpoint)
            global passes
            passes += 1
            return r.json()
        except Exception as e:
            print("\033[91m {}\033[00m" .format("FAILED: "), end="")
            print(endpoint)
            print("Exception occured while processing:")
            traceback.print_exc()

            print("Expected response:", expected_response)
            print("Got response:", r.json())
            print("Status code:", r.status_code)
            #global fails
            fails += 1



ver = do_test("GET", "")
print("="*10 + "ROYAL AUTOMATION BACKEND TEST" + "="*10)
print("VERSION:", ver['Version'])
user = do_test("POST", "add_user", {"email": USERNAME, "name": "sanity"}, data={
  "email": USERNAME,
  "name": "sanity",
  "password": PASSWORD
})


id = user["id"]
do_test("GET", f"get_user/{USERNAME}", expected_response=user)

HOUSENAME1 = "hn1_"
house = do_test("POST", f"add_house/{id}", expected_response={"name" : HOUSENAME1, "owner_id": id}, data={
  "name": HOUSENAME1
})

houses = do_test("GET", f"get_houses/{id}")
assert len(houses) == 1, "get_houses is not working"


house_id = houses[0]["id"]

house2 = do_test("POST", f"change_house_name/{house_id}/hn2", expected_response={"name" : "hn2", "owner_id": id, "id" : house_id})


## Devices
device1 = do_test("POST", f"add_device/{house_id}", data={
  "name": "dev1_",
  "serial_number": 1,
  "type": "device"
}, expected_response={
  "name": "dev1_",
  "serial_number": 1,
  "type": "device",
  "house_id": house_id
})

device2 = do_test("POST", f"add_device/{house_id}", data={
  "name": "dev2_",
  "serial_number": 2,
  "type": "sensor"
}, expected_response={
  "name": "dev2_",
  "serial_number": 2,
  "type": "sensor",
  "house_id": house_id
})

devices_all = do_test("GET", f"get_devices/{house_id}")
assert device1 in devices_all, "Device1 not added correctly"
assert device2 in devices_all, "Device2 not added correctly"


device2 = do_test("POST", f"change_device_name/{device2['id']}/dev2_new", data={
  "name": "dev2",
  "serial_number": 2,
  "type": "sensor"
}, expected_response={
  "name": "dev2_new",
  "serial_number": 2,
  "type": "sensor",
  "house_id": house_id,
  "id": device2["id"]
})
# Add rules and schedule
rule1 = do_test("POST", f"add_rule/{house_id}", data={
  "sensor_sn": 2,
  "device_sn": 1,
  "value": 100,
  "activation_value": 0,
  "condition": "le"
}, expected_response={
  "sensor_sn": 2,
  "device_sn": 1,
  "value": 100,
  "activation_value": 0,
  "condition": "le",
  "house_id" : house_id
})
rules_all = do_test("GET", f"get_rules/{house_id}")
assert rule1 in rules_all, "Rule1 not added correctly"
rule2 = do_test("POST", f"update_rule/{house_id}/{rule1['id']}", data={
  "sensor_sn": 2,
  "device_sn": 1,
  "value": 0,
  "activation_value": 0,
  "condition": "le"
}, expected_response={
  "sensor_sn": 2,
  "device_sn": 1,
  "value": 0,
  "activation_value": 0,
  "condition": "le"
})
rules_all = do_test("GET", f"get_rules/{house_id}")
assert rule2 in rules_all, "Rule2 not added correctly"

sched1 = do_test("POST", f"add_schedule/{house_id}", data={
  "time_hours": 10,
  "time_minutes": 10,
  "device_id": 1,
  "value": 0,
  "repeat": "1234567"
}, expected_response={
  "time_hours": 10,
  "time_minutes": 10,
  "device_id": 1,
  "value": 0,
  "repeat": "1234567"
})

sched_all = do_test("GET", f"get_schedule_items/{house_id}")
assert sched1 in sched_all, "Sched1 not added correctly"
do_test("DELETE", F"del_schedule/{sched1['id']}", expected_response={'status':'OK'})

do_test("POST", "operate_device", data={
  "serial_number": 1,
  "value": 0
}, expected_response={'status': 'OK'})

do_test("DELETE", f"del_rule/{rule2['id']}", expected_response={'status':'OK'})

do_test("DELETE", f"del_device/{device1['id']}", expected_response={'status': 'OK'})
do_test("DELETE", f"del_device/{device2['id']}", expected_response={'status': 'OK'})

for house in houses:
    do_test("DELETE", f"del_house/{house['id']}", expected_response={'status': 'OK'})

do_test("DELETE", f"del_user/{user['id']}", expected_response={'status': 'OK'})


print("FINISHED TEST SESSION")
print("Passes:           ", passes)
print("Fails:            ", fails)
print("N/A:              ", n_a)
print("Total tests done: ", passes + fails + n_a)