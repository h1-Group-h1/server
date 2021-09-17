import requests
from requests.auth import HTTPBasicAuth
import argparse


admin_username = "admin"
admin_passwd = "ojifojsaodfiosdnnewoinin23132139nj3kln2k9u3209kln"
BASE_URL = "https://com-ra-api.co.uk/"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manager for devices")
    parser.add_argument('command', metavar="COMMAND", type=str, help="Command to use: list (lists devices) or add (adds devices) ", choices=["list", "add"])
    args = parser.parse_args()
    print(args.command)
    r = requests.post(BASE_URL + "add_user/", json={
  "email": "admin",
  "name": "ADMIN",
  "password": "ojifojsaodfiosdnnewoinin23132139nj3kln2k9u3209kln"
})
    r = requests.get(BASE_URL +"admin/get_access_key", auth=HTTPBasicAuth(admin_username, admin_passwd))

    if r.status_code != 200:
        print(r.json())
    access_key = input("Enter access key: ")

    if args.command == "list":
        r = requests.get(BASE_URL + f'admin/{access_key}/get_registered_devices', auth=HTTPBasicAuth(admin_username, admin_passwd))
        print(*(r.json()), sep=", ")
    else:
        buf: str = ""
        while True:
            device_sn = input("Enter device serial number: ")
            if device_sn == "-1":
                break
            device_passwd = input("Enter assigned password: ")
            r = requests.post(BASE_URL + f'admin/{access_key}/add_device/{device_sn}/{device_passwd}', auth=HTTPBasicAuth(admin_username, admin_passwd))
            if r.status_code != 200:
                print("Failed to add device:", r.json())

        r = requests.post(BASE_URL + f'admin/{access_key}/restart_broker', auth=HTTPBasicAuth(admin_username, admin_passwd))
        if r.status_code != 200:
            print("Failed to start broker")
