from typing import List

from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from threading import Thread

import crud
import models
import schemas
from database import SessionLocal, engine
import constants
from devices import mqtt_main, notify_device

import logging

logging.basicConfig(level=logging.DEBUG, filename='../data/app_log.log')

if constants.debug:
    models.Base.metadata.drop_all(engine)
models.Base.metadata.create_all(bind=engine)

mqtt = Thread(target=mqtt_main)
mqtt.start()
app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get('/')
def root():
    return {'Hello': 'World'}


@app.post('/add_device/{house_id}', response_model=schemas.Device)  # OK
def add_device(house_id: int, device: schemas.DeviceCreate, db: Session = Depends(get_db)):
    # Add device, return created id
    db_device = crud.get_device_by_sn(db, device.serial_number)
    if db_device:
        raise HTTPException(status_code=400, detail="Device already added to database")
    return crud.create_house_device(db, device, house_id)


@app.delete('/del_device/{device_id}')  # OK
def del_device(device_id: int, db: Session = Depends(get_db)):
    # Delete device and return status
    result = crud.delete_device(db, device_id)
    if result < 0:
        raise HTTPException(status_code=400, detail="Unable to delete device from server")
    return {"status": "OK"}


@app.post('/add_user/', response_model=schemas.User)  # OK
def add_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Add user and return unique code
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.get("/get_users/", response_model=List[schemas.User])  # OK
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get('/get_user/{email}', response_model=schemas.User)  # OK
def get_user(email: str, db: Session = Depends(get_db)):
    # Check if there is user
    db_user = crud.get_user_by_email(db, email=email)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post('/operate_device/')
def operate_device(action: schemas.DeviceAction, db: Session = Depends(get_db)):
    # Operate the device
    try:
        device_sn = crud.get_device(db, action.id).serial_number
        notify_device(str(device_sn), action.value.to_bytes(1, "big"))
        return {"status": "OK"}
    except:
        raise HTTPException(status_code=400, detail="Unable to operate device")


@app.post('/add_rule/{house_id}', response_model=schemas.Rule)  # OK
def add_rule(house_id: int, rule: schemas.RuleCreate, db: Session = Depends(get_db)):
    # Add the rule
    db_rule = crud.create_house_rule(db, rule=rule, house_id=house_id)
    print("OK")
    # Notify the device
    cond_i = 0
    if rule.condition == "gr":
        cond_i = 0
    elif rule.condition == "eq":
        cond_i = 1
    elif rule.condition == "le":
        cond_i = 2
    else:
        raise HTTPException(status_code=400, detail="Invalid value for condition: {0}".format(rule.condition))
    val = rule.value
    rule_id = db_rule.id
    print(cond_i.to_bytes(1, "little"))
    payload = (cond_i | (val >> 8) | (rule_id >> 16)).to_bytes(6, "little")
    print(payload)
    notify_device(str(rule.sensor_id), payload)
    return db_rule


@app.delete('/del_rule/{rule_id}')  # OK
def del_rule(rule_id: int, db: Session = Depends(get_db)):
    db_rule = crud.get_rule(db, rule_id)
    if db_rule is None:
        raise HTTPException(status_code=400, detail="Cannot find rule in database")
    cond_i = 3
    val = 0
    rule_id = db_rule.id
    payload = (cond_i | (val >> 8) | (rule_id >> 16)).to_bytes(6, "little")
    notify_device(str(db_rule.sensor_id), payload)
    res = crud.delete_rule(db, rule_id)
    if res < 0:
        raise HTTPException(status_code=400, detail="Rule cannot be deleted")
    # Notify device
    return {"status": "OK"}


@app.get('/get_rules/{house_id}', response_model=List[schemas.Rule])  # OK
def get_rules(house_id: int, db: Session = Depends(get_db)):
    # Get rules
    db_rules = crud.get_rules_by_house(db, house_id)
    if db_rules is None:
        raise HTTPException(status_code=404, detail="No rules found for house")
    return db_rules


@app.post('/set_schedule/{device_id}')
def set_schedule(device_id: int, schedule: schemas.ScheduleItem, db: Session = Depends(get_db)):
    # Set schedule, communicate to devices
    type = 1
    val = schedule.action.value
    payload = (type | (val >> 8) | (schedule.time_hours >> 16) | (schedule.time_minutes >> 24)).to_bytes(4, "little")

    db_device = crud.get_device(db, schedule.action.id)
    notify_device(str(db_device.serial_number), payload)


@app.get('/get_devices/{house_id}', response_model=List[schemas.Device])  # OK
def get_devices(house_id: int, db: Session = Depends(get_db)):
    # Get a list of devices
    db_devices = crud.get_devices_by_house(db, house_id)
    if db_devices is None:
        raise HTTPException(status_code=404, detail="No devices found for user")
    return db_devices


@app.get('/get_houses/{user_id}', response_model=List[schemas.House])  # OK
def get_houses(user_id: int, db: Session = Depends(get_db)):
    # Get houses
    db_houses = crud.get_houses_by_owner(db, user_id)
    if db_houses is None:
        raise HTTPException(status_code=404, detail="User does not have any houses")
    return db_houses


@app.post('/add_house/{user_id}', response_model=schemas.House)  # OK
def add_house(user_id: int, house: schemas.HouseCreate, db: Session = Depends(get_db)):  # OK
    new_house = crud.create_user_house(db=db, house=house, user_id=user_id)
    if new_house is None:
        raise HTTPException(status_code=400, detail="House with same name already added")
    return new_house


@app.delete('/del_house/{house_id}')  # OK
def del_house(house_id: int, db: Session = Depends(get_db)):
    res = crud.delete_house(db, house_id)
    if res < 0:
        raise HTTPException(status_code=400, detail="Unable to delete house")
    return {"status": "OK"}


@app.post('/update_rule/{house_id}/{rule_id}', response_model=schemas.Rule)  # OK
def update_rule(house_id: int, rule_id: int, new_rule: schemas.RuleCreate, db: Session = Depends(get_db)):
    # Delete rule and add
    del_rule(rule_id, db)
    return add_rule(house_id, new_rule, db)


@app.get('/device_status/{device_id}', response_model=schemas.DeviceStatus)  # id is the database id
def get_device(device_id: int, db: Session = Depends(get_db)):
    return {"status": crud.get_device(db, device_id).status}
