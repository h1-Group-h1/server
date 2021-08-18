from typing import List
import secrets

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session
import paho.mqtt.client as mqtt

import crud
import models
import schemas
from database import SessionLocal, engine
from constants import *
import time
import os
import hashlib


models.Base.metadata.drop_all(engine)
models.Base.metadata.create_all(bind=engine)

client = mqtt.Client()


def log(msg, type=constants.info):
    type_desc = "INFO"
    if type == constants.error:
        type_desc = "ERROR"
    elif type == constants.warning:
        type_desc = "WARNING"

    print((
        time.strftime("[%d %m %Y, %H:%M:%S]", time.localtime()
                      ) + " " + type_desc + ": " + msg
    ), file=open('/tmp/app_log.log', 'a'))


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_normal():
    return next(get_db())


def notify_device(device: str, payload: bytes):
    global client
    client.publish("devices/" + device, payload)


def on_connect(client, userdata, flags, rc):
    print("MQTT client connected")
    client.subscribe("server/sensors/#")
    client.subscribe("server/remotes/#")
    # server/# --> Data from devices to server
    # devices/# --> Data from server to devices


def on_message(client, userdata, msg):
    if msg.topic.startswith("devices/sensors") or msg.topic.startswith("devices/remotes"):
        print(msg.topic)
        sn = int(msg.topic.split('/')[2])
        if msg.topic.startswith("devices/sensors"):
            db = get_db_normal()
            # db_device = crud.get_device_by_sn(db, sn)
            db_rule = crud.get_rule(db, int(msg.payload))
            if db_rule:
                notify_device(str(sn), db_rule.value)
        elif msg.topic.startswith("devices/remotes"):  # Ignore for now
            # Remote pressed
            remote_sn = msg.topic.split('/')[-1]
            raw = msg.payload.encode("utf-8")
            command = int(raw[0])
            sn = int(raw[1:5])
            value = int(raw[5])
            if command == 0x1:
                notify_device(str(sn), (value >> 8).to_bytes(
                    4, "little"))  # Arduino is little-endian
            else:
                # Get devices and send
                db = get_db_normal()
                db_house = crud.get_device_house(db, sn)
                db_devices = crud.get_devices_by_house(db, db_house.house_id)
                for device in db_devices:
                    print("Sending:", device.serial_number, "name:", device.name)
                    payload = device.name + "@" + str(device.serial_number)
                    notify_device(remote_sn, bytes(payload))


def hash_password(password, salt=None):
    if salt == None:
        salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        100000
    )
    return key + ":" + salt


def compare_password_hash(user_password, db_password):
    # get the salt from the db_password
    key_salt = db_password.split(":")
    # hash the password using the salt
    hashed_password = hash_password(user_password, key_salt[1])
    return (hash_password == db_password)


client.on_connect = on_connect
client.on_message = on_message
client.connect("com-ra-api.co.uk")
client.loop_start()
print("MQTT client started")

app = FastAPI()
security = HTTPBasic()


def get_current_username(credentials: HTTPBasicCredentials = Depends(security),
                         db: Session = Depends(get_db)):
    # Username is email
    username_result = crud.get_user_by_email(db, credentials.username)
    if not username_result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    db_username = username_result.email
    db_password = username_result.hashed_password
    correct_username = secrets.compare_digest(
        credentials.username, db_username)
    # correct_password = secrets.compare_digest(credentials.password, db_password) #Old method; before hashing was added
    # new method:
    correct_password = compare_password_hash(credentials.password, db_password)
    if not (correct_username and correct_password):
        log(f"Bad username: {db_username} with password: {db_password}", warning)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


@app.get('/')
def root():
    return {'Hello': 'World'}


@app.post('/add_device/{house_id}', response_model=schemas.Device)  # OK
def add_device(house_id: int, device: schemas.DeviceCreate, db: Session = Depends(get_db),
               username: str = Depends(get_current_username)):
    # Add device, return created id
    db_device = crud.get_device_by_sn(db, device.serial_number)
    if db_device:
        raise HTTPException(
            status_code=400, detail="Device already added to database")
    db_device_by_name = crud.get_device_by_name_and_house_id(
        db, device.name, house_id)
    if db_device_by_name:
        raise HTTPException(
            status_code=400, detail="Device with same name in database")

    db_user = crud.get_user_by_email(db, username)
    db_houses = crud.get_houses_by_owner(db, db_user.id)
    for house in db_houses:
        if house.id == house_id:  # Checks if the house is part of the user
            if device.type not in [DEVICE_SENSOR, DEVICE_DEVICE]:
                raise HTTPException(
                    status_code=400, detail=f"Incorrect device type {device.type}")
            log(f"Added device: {device.serial_number}", info)
            return crud.create_house_device(db, device, house_id)
    raise HTTPException(status_code=400, detail="Unable to add device")


@app.delete('/del_device/{device_id}')  # OK
def del_device(device_id: int, db: Session = Depends(get_db),
               username: str = Depends(get_current_username)):
    # Delete device and return status
    device_user = crud.get_device_owner(db, device_id)
    if device_user and device_user.email == username:
        result = crud.delete_device(db, device_id)
        if result < 0:
            raise HTTPException(
                status_code=400, detail="Unable to delete device from server")
        log(f"Deleted device {device_id}", info)
        return {"status": "OK"}
    raise HTTPException(
        status_code=400, detail="Unable to delete device from server")


@app.post('/add_user/', response_model=schemas.User)  # OK
def add_user(user: schemas.UserCreate, db: Session = Depends(get_db)):

    # hash the user's password
    user.hashed_password = hash_password(user.hashed_password)

    # Add user and return unique code
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.get('/get_user/{email}', response_model=schemas.User)  # OK
def get_user(email: str, db: Session = Depends(get_db), username: str = Depends(get_current_username)):
    # Check if there is user
    db_user: schemas.User = crud.get_user_by_email(db, email=email)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.delete('/del_user/{user_id}')
def del_user(user_id: int, db: Session = Depends(get_db), username: str = Depends(get_current_username)):
    db_user = crud.get_user(db, user_id)
    if db_user and db_user.email == username:
        res = crud.delete_user(db, user_id)
        if res < 0:
            raise HTTPException(
                status_code=400, detail="Unable to delete user")
        return {"status": "OK"}
    raise HTTPException(status_code=400, detail="Unable to delete user")


@app.post('/operate_device/')
def operate_device(action: schemas.DeviceAction, db: Session = Depends(get_db),
                   username: str = Depends(get_current_username)):
    # Operate the device
    try:
        db_device = crud.get_device_by_sn(db, action.serial_number)
        device_user = crud.get_device_owner(db, db_device.id)
        print(device_user)
        if device_user and device_user.email == username and db_device.type == DEVICE_DEVICE:
            # Secrets.compare_digest()?
            payload = schemas.OperationCommand(
                val=action.value
            )
            notify_device(str(action.serial_number), bytes(
                payload.json(), encoding='utf-8'))
            return {"status": "OK", "device": str(action.serial_number)}
    except:
        raise HTTPException(status_code=400, detail="Unable to operate device")


@app.post('/add_rule/{house_id}', response_model=schemas.Rule)  # OK
def add_rule(house_id: int, rule: schemas.RuleCreate, db: Session = Depends(get_db),
             username: str = Depends(get_current_username)):
    # Add the rule
    db_device = crud.get_device_by_sn(db, rule.device_sn)
    db_sensor = crud.get_device_by_sn(db, rule.sensor_sn)
    db_device_user = crud.get_device_owner(db, db_device.id)
    db_sensor_user = crud.get_device_owner(db, db_sensor.id)
    if not db_device_user or not db_sensor_user \
            or db_sensor_user.email != username or db_device_user.email != username \
            or db_device.type != DEVICE_DEVICE or db_sensor.type != DEVICE_SENSOR:
        raise HTTPException(status_code=400, detail="Unable to set rule")

    print("OK")
    # Notify the device
    if rule.condition not in ["gr", "le", "eq"]:
        raise HTTPException(
            status_code=400, detail="Invalid value for condition: {0}".format(rule.condition))

    db_rule = crud.create_house_rule(db, rule=rule, house_id=house_id)
    payload = schemas.AddRuleCommand(
        condition=db_rule.condition,
        raw_value=db_rule.value,
        rule_id=db_rule.id
    )
    notify_device(str(rule.sensor_sn), bytes(payload.json(), encoding='utf-8'))
    return db_rule


@app.delete('/del_rule/{rule_id}')  # OK
def del_rule(rule_id: int, db: Session = Depends(get_db),
             username: str = Depends(get_current_username)):
    db_rule = crud.get_rule(db, rule_id)
    if db_rule is None:
        raise HTTPException(
            status_code=400, detail="Cannot find rule in database")
    db_user = crud.get_house_owner(db, db_rule.house_id)

    if db_user.email != username:
        raise HTTPException(status_code=400, detail="Unable to delete rule")

    payload = schemas.DelRuleCommand(
        rule_id=rule_id
    )
    notify_device(str(db_rule.sensor_sn), bytes(
        payload.json(), encoding='utf-8'))
    res = crud.delete_rule(db, db_rule.id)
    if res < 0:
        raise HTTPException(status_code=400, detail="Rule cannot be deleted")
    return {"status": "OK"}


@app.get('/get_rules/{house_id}', response_model=List[schemas.Rule])  # OK
def get_rules(house_id: int, db: Session = Depends(get_db),
              username: str = Depends(get_current_username)):
    # Get rules
    db_user = crud.get_house_owner(db, house_id)
    if db_user and db_user.email == username:

        db_rules = crud.get_rules_by_house(db, house_id)
        if db_rules is None:
            raise HTTPException(
                status_code=404, detail="No rules found for house")
        return db_rules
    raise HTTPException(status_code=400, detail="Unable to return rules")


@app.post('/add_schedule')
def add_schedule(schedule: schemas.ScheduleCreate, db: Session = Depends(get_db),
                 username: str = Depends(get_current_username)):
    # Set schedule, communicate to devices
    db_device = crud.get_device(db, schedule.device_id)
    if not db_device:
        raise HTTPException(status_code=400, detail="Unable to set schedule")

    db_user = crud.get_device_owner(db, db_device.id)
    if db_user and db_user.email == username:
        db_schedule = crud.create_schedule_item(db, schedule)
        # Add schedule to database
        payload = schemas.AddScheduleCommand(
            value=schedule.value,
            th=schedule.time_hours,
            tm=schedule.time_minutes,
            schedule_id=db_schedule.id,
            repeat=db_schedule.repeat
        )
        print(payload.json())

        notify_device(str(db_device.serial_number),
                      bytes(payload.json(), encoding='utf-8'))
        return db_schedule
    raise HTTPException(status_code=400, detail="Unable to set schedule")


@app.delete('/del_schedule/{schedule_id}')
def del_schedule(schedule_id: int, db: Session = Depends(get_db), username: str = Depends(get_current_username)):
    # Delete schedule
    db_user = crud.get_schedule_owner(db, schedule_id)
    if db_user and db_user.email == username:
        db_schedule = crud.get_schedule_item(db, schedule_id)
        db_device = crud.get_device(db, db_schedule.device_id)
        notify_device(str(db_device.serial_number), bytes(schemas.DelScheduleCommand(
            schedule_id=schedule_id
        ).json(), encoding='utf-8'))
        crud.delete_schedule_item(db, schedule_id)
        return {"status": "OK"}
    raise HTTPException(status_code=400, detail="Unable to delete schedule")


@app.get('/get_schedule_items/{house_id}', response_model=List[schemas.Schedule])
def get_schedule_items(house_id: int, db: Session = Depends(get_db), username: str = Depends(get_current_username)):
    db_user = crud.get_house_owner(db, house_id)
    if db_user and db_user.email == username:
        return crud.get_schedule_items_by_house(db, house_id)


@app.get('/get_devices/{house_id}', response_model=List[schemas.Device])  # OK
def get_devices(house_id: int, db: Session = Depends(get_db),
                username: str = Depends(get_current_username)):
    # Get a list of devices
    db_user = crud.get_house_owner(db, house_id)
    if db_user and db_user.email == username:

        db_devices = crud.get_devices_by_house(db, house_id)
        if db_devices is None:
            raise HTTPException(
                status_code=404, detail="No devices found for user")
        return db_devices
    raise HTTPException(status_code=400, detail="Unable to return devices")


@app.get('/get_houses/{user_id}', response_model=List[schemas.House])  # OK
def get_houses(user_id: int, db: Session = Depends(get_db),
               username: str = Depends(get_current_username)):
    # Get houses
    db_user = crud.get_user(db, user_id)
    if not db_user or db_user.email != username:
        raise HTTPException(status_code=400, detail="Unable to return houses")
    db_houses = crud.get_houses_by_owner(db, user_id)
    if db_houses is None:
        raise HTTPException(
            status_code=404, detail="User does not have any houses")
    return db_houses


@app.post('/add_house/{user_id}', response_model=schemas.House)  # OK
def add_house(user_id: int, house: schemas.HouseCreate, db: Session = Depends(get_db),
              username: str = Depends(get_current_username)):  # OK
    db_user = crud.get_user(db, user_id)
    if not db_user or db_user.email != username:
        raise HTTPException(status_code=400, detail="Unable to add house")
    new_house = crud.create_user_house(db=db, house=house, user_id=user_id)
    if new_house is None:
        raise HTTPException(
            status_code=400, detail="House with same name already added")
    return new_house


@app.delete('/del_house/{house_id}')  # OK
def del_house(house_id: int, db: Session = Depends(get_db),
              username: str = Depends(get_current_username)):
    house_owner = crud.get_house_owner(db, house_id)
    if house_owner and house_owner.email == username:
        res = crud.delete_house(db, house_id)
        if res < 0:
            raise HTTPException(
                status_code=400, detail="Unable to delete house")
        return {"status": "OK"}
    raise HTTPException(status_code=400, detail="Unable to delete house")


# OK
@app.post('/update_rule/{house_id}/{rule_id}', response_model=schemas.Rule)
def update_rule(house_id: int, rule_id: int, new_rule: schemas.RuleCreate, db: Session = Depends(get_db),
                username: str = Depends(get_current_username)):
    # Delete rule and add
    del_rule(rule_id, db, username)
    return add_rule(house_id, new_rule, db, username)


# Not needed now
@app.post('/add_remote/{house_id}/{remote_sn}')
def add_remote(house_id: int, remote_sn: int,
               username: str = Depends(get_current_username)):
    # Send a message to the remote
    payload = house_id.to_bytes(6, "little") + b'00'  # Checksum
    notify_device(str(remote_sn), payload)  # Payload later


@app.post('/change_device_name/{device_id}/{new_name}', response_model=schemas.Device)
def change_device_name(device_id: int, new_name: str, db: Session = Depends(get_db),
                       username: str = Depends(get_current_username)):
    device_owner = crud.get_device_owner(db, device_id)
    db_device = crud.get_device(db, device_id)
    if device_owner and device_owner.email == username and db_device:
        return crud.update_device_name(db, device_id, new_name)
    raise HTTPException(status_code=400, detail="Unable to update name")


@app.post('/change_house_name/{house_id}/{new_name}', response_model=schemas.House)
def change_house_name(house_id: int, new_name: str, db: Session = Depends(get_db),
                      username: str = Depends(get_current_username)):
    house_owner = crud.get_house_owner(db, house_id)
    db_house = crud.get_house(db, house_id)
    if house_owner and db_house and house_owner.email == username:
        return crud.update_house_name(db, house_id, new_name)
    raise HTTPException(status_code=400, detail="Unable to update name")


@app.post('/relay_status/{house_id}')
def relay_status(house_id: int, db: Session = Depends(get_db), username: str = Depends(get_current_username)):
    house_owner = crud.get_house_owner(db, house_id)
    db_house = crud.get_house(db, house_id)
    if house_owner and db_house and house_owner.email == username:
        db_devices = crud.get_devices_by_house(db, house_id)
        for device in db_devices:
            notify_device(str(device.serial_number), bytes(
                schemas.RelayStatusCommand().json(), encoding='utf-8'))
        return {"status": "OK"}
    raise HTTPException(status_code=400, detail="Unable to notify status")
