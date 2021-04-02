from typing import List

from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session

import crud
import models
import schemas
from database import SessionLocal, engine

models.Base.metadata.drop_all(engine)
models.Base.metadata.create_all(bind=engine)


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


@app.post('/add_device/{house_id}', response_model=schemas.Device)
def add_device(house_id: int, device: schemas.DeviceCreate, db: Session = Depends(get_db)):
    # Add device, return created id
    db_device = crud.get_device_by_sn(db, device.serial_number)
    if db_device:
        raise HTTPException(status_code=400, detail="Device already added to database")
    return crud.create_house_device(db, device, house_id)


@app.delete('/del_device/{device_id}')
def del_device(device_id: int, db: Session = Depends(get_db)):
    # Delete device and return status
    result = crud.delete_device(db, device_id)
    if result < 0:
        raise HTTPException(status_code=400, detail="Unable to delete device from server")
    return {"status": "OK"}


@app.post('/add_user/', response_model=schemas.User)
def add_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Add user and return unique code
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.get("/get_users/", response_model=List[schemas.User])
def read_users(skip:int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get('/get_user/{email}', response_model=schemas.User)
def get_user(email: str, db: Session = Depends(get_db)):
    # Check if there is user
    db_user = crud.get_user_by_email(db, email=email)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post('/operate_device/')
def operate_device(action: schemas.DeviceAction):
    # Operate the device
    pass


@app.post('/add_rule/{house_id}', response_model=schemas.Rule)
def add_rule(house_id: int, rule: schemas.RuleCreate, db: Session = Depends(get_db)):
    # Add the rule
    return crud.create_house_rule(db, rule=rule, house_id=house_id)


@app.delete('/del_rule/{rule_id}')
def del_rule(rule_id: int, db: Session = Depends(get_db)):
    res = crud.delete_rule(db, rule_id)
    if res < 0:
        raise HTTPException(status_code=400, detail="Rule cannot be deleted")
    return {"status": "OK"}


@app.get('/get_rules/{house_id}', response_model=List[schemas.Rule])
def get_rules(house_id: int, db: Session = Depends(get_db)):
    # Get rules
    db_rules = crud.get_rules_by_house(db, house_id)
    if db_rules is None:
        raise HTTPException(status_code=404, detail="No rules found for house")
    return db_rules


@app.post('/set_schedule/{device_id}')
def set_schedule(device_id: int, schedule: schemas.ScheduleItem):
    # Set schedule, communicate to devices
    pass


@app.get('/get_devices/{house_id}', response_model=List[schemas.Device])
def get_devices(house_id: int, db: Session = Depends(get_db)):
    # Get a list of devices
    db_devices = crud.get_devices_by_house(db, house_id)
    if db_devices is None:
        raise HTTPException(status_code=404, detail="No devices found for user")
    return db_devices


@app.get('/get_houses/{user_id}', response_model=List[schemas.User])
def get_houses(user_id: int, db: Session = Depends(get_db)):
    # Get houses
    db_houses = crud.get_houses_by_owner(db, user_id)
    if db_houses is None:
        raise HTTPException(status_code=404, detail="User does not have any houses")
    return db_houses


@app.post('/add_house/{user_id}', response_model=schemas.House)
def add_house(user_id: int, house: schemas.HouseCreate, db: Session = Depends(get_db)):
    # Mobile app responsibility to check if house exists.
    return crud.create_user_house(db=db, house=house, user_id=user_id)


@app.delete('/del_house/{house_id}')
def del_house(house_id: int, db: Session = Depends(get_db)):
    res = crud.delete_house(db, house_id)
    if res < 0:
        raise HTTPException(status_code=400, detail="Unable to delete house")
    return {"status": "OK"}


@app.post('/update_rule/{house_id}/{rule_id}', response_model=schemas.Rule)
def update_rule(house_id: int, rule_id: int, new_rule: schemas.RuleCreate, db: Session = Depends(get_db)):
    # Delete rule and add
    crud.delete_rule(db, rule_id)
    return crud.create_house_rule(db, new_rule, house_id)
