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
    r = requests.get(BASE_URL + "/admin/get_access_key", auth=HTTPBasicAuth(admin_username, admin_passwd))

    print(r.response)
    access_key = input("Enter access key: ")
