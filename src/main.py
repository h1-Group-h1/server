from typing import Optional
from fastapi import FastAPI
from data import *

app = FastAPI()


@app.get('/')
def root():
    return {'Hello': 'World'}


@app.post('/add_device')
def add_device(device: Device):
    # Add device, return created id
    res = ""
    return res


@app.delete('/del_device')
def del_device(id: Device):
    # Delete device and return status
    res = ""
    return res


@app.post('/add_user')
def add_user(data: User):
    # Add user and return unique code
    res = ""
    return res


@app.get('/get_user/{email}')
def get_user(email: str):
    # Check if there is user
    res = ""
    return res


@app.post('/operate_device')
def operate_device(action: DeviceAction):
    # Operate the device
    res = ""
    return res


@app.post('/add_rule')
def add_rule(rule: DeviceRule):
    # Add the rule
    res = ""
    return res


@app.delete('/del_rule')
def del_rule(rule: RuleId):
    # Delete rule
    res = ""
    return res


@app.get('/get_rules/{user_id}/{house_id}')
def get_rules(user_id: int, house_id: int):
    # Get rules
    res = ""
    return res


@app.post('/set_schedule')
def set_schedule(schedule: ScheduleItem):
    # Set schedule

    res = ""
    return res


@app.get('/get_devices/{user_id}/{house_id}')
def get_devices(user_id: int, house_id: int):
    # Get a list of devices

    res = ""
    return res


@app.get('/get_houses/{user_id}')
def get_houses(user_id: int):
    # Get houses
    res = ""
    return res


@app.post('/add_house')
def add_house(house: NewHouse):
    res = ""
    return res


@app.delete('/del_house')
def del_house(house: ExistingHouse):
    res = ""
    return res
