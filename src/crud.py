from sqlalchemy.orm import Session

import models
import schemas
import random

def create_random_string(length: int):
    string = ""
    for i in range(length):
        string += chr(random.randint(65, 122))
    return string
    


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 0):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    broker_password = create_random_string(255)
    db_user = models.User(email=user.email, name=user.name, password=user.password, broker_username="client-"+user.email, broker_password=broker_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


def get_house(db: Session, house_id: int):
    return db.query(models.House).filter(models.House.id == house_id).first()


def get_houses(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.House).offset(skip).limit(limit).all()


def get_house_owner(db: Session, house_id: int):
    db_house = get_house(db, house_id)
    if db_house:
        return get_user(db, db_house.owner_id)


def get_houses_by_owner(db: Session, owner_id: int):
    return db.query(models.House).filter(models.House.owner_id == owner_id).all()


def get_houses_by_owner_and_name(db: Session, owner_id: int, house_name: str):
    return db.query(models.House).filter(models.House.owner_id == owner_id and models.House.name == house_name).first()


def create_user_house(db: Session, house: schemas.HouseCreate, user_id: int):
    prev_house = db.query(models.House).filter(models.House.name == house.name).first()
    if prev_house:
        return None
    db_house = models.House(**house.dict(), owner_id=user_id)
    db.add(db_house)
    db.commit()
    db.refresh(db_house)
    return db_house


def get_device(db: Session, device_id: int):
    return db.query(models.Device).filter(models.Device.id == device_id).first()


def get_device_by_sn(db: Session, device_sn: int):
    return db.query(models.Device).filter(models.Device.serial_number == device_sn).first()


def get_device_by_name_and_house_id(db: Session, name: str, house_id: int):
    return db.query(models.Device).filter(models.Device.name == name and models.Device.house_id == house_id) \
        .first()


def get_devices_by_house(db: Session, house_id: int):
    return db.query(models.Device).filter(models.Device.house_id == house_id).all()


def get_device_house(db: Session, device_sn: int):
    return db.query(models.Device).filter(models.Device.serial_number == device_sn).first()


def get_device_owner(db: Session, device_id: int):
    device = db.query(models.Device).filter(models.Device.id == device_id).first()
    if device:
        print("Device found")
        house = get_house(db, device.house_id)
        if house:
            print("House found")
            return get_user(db, house.owner_id)


def create_house_device(db: Session, device: schemas.DeviceCreate, house_id: int):
    db_device = models.Device(**device.dict(), house_id=house_id)
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    return db_device


def get_rule(db: Session, id: int):
    return db.query(models.Rule).filter(models.Rule.id == id).first()


def get_rules_by_house(db: Session, house_id: int):
    return db.query(models.Rule).filter(models.Rule.house_id == house_id).all()


def create_house_rule(db: Session, rule: schemas.RuleCreate, house_id: int):
    db_rule = models.Rule(**rule.dict(), house_id=house_id)
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    return db_rule


def get_rule_device(db: Session, rule_id: int, device: int):
    return db.query(models.Rule).filter(models.Rule.id == rule_id).first().device


def delete_item(db: Session, get_fn, id: int):
    item = get_fn(db, id)
    if not item:
        return -1
    db.delete(item)
    db.commit()
    return 0


def delete_device(db: Session, device_id: int):
    return delete_item(db, get_device, device_id)


def delete_house(db: Session, house_id: int):
    return delete_item(db, get_house, house_id)


def delete_rule(db: Session, rule_id: int):
    return delete_item(db, get_rule, rule_id)


def delete_user(db: Session, user_id: int):
    return delete_item(db, get_user, user_id)


def update_rule(db: Session, rule_id: int, newRule: schemas.RuleCreate):
    db.query(models.Rule).filter(models.Rule.id == rule_id) \
        .update({models.Rule.sensor_sn: newRule.sensor_sn,
                 models.Rule.value: newRule.value,
                 models.Rule.activation_value: newRule.activation_value,
                 models.Rule.condition: newRule.condition,
                 models.Rule.device_sn: newRule.device_sn}, synchronize_session=False)
    db.commit()
    return get_rule(db, rule_id)

def update_device_name(db: Session, device_id: int, new_name: str):
    db.query(models.Device).filter(models.Device.id == device_id) \
        .update({models.Device.name: new_name}, synchronize_session=False)
    db.commit()
    return get_device(db, device_id)


def update_house_name(db: Session, house_id: int, new_name: str):
    db.query(models.House).filter(models.House.id == house_id) \
        .update({models.House.name: new_name}, synchronize_session=False)
    db.commit()
    return get_house(db, house_id)


def create_schedule_item(db: Session, schedule: schemas.ScheduleCreate, house_id: int):
    db_schedule = models.Schedule(**schedule.dict(), house_id=house_id)
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    return db_schedule


def get_schedule_item(db: Session, schedule_id: int):
    return db.query(models.Schedule).filter(models.Schedule.id == schedule_id).first()


def delete_schedule_item(db: Session, schedule_id: int):
    return delete_item(db, get_schedule_item, schedule_id)


def get_schedule_owner(db: Session, schedule_id: int):
    db_schedule = get_schedule_item(db, schedule_id)
    if db_schedule:
        return get_house_owner(db, db_schedule.house_id)

def get_schedule_items_by_house(db: Session, house_id: int):
    return db.query(models.Schedule).filter(models.Schedule.house_id == house_id).all()


def get_device_broker_password(db: Session, serial_number: int):
    return db.query(models.DeviceLog).filter(models.DeviceLog.serial_number == serial_number).first().broker_password


def get_device_log(db: Session, serial_number: int):
    return db.query(models.DeviceLog).filter(models.DeviceLog.serial_number == serial_number).first()

def add_device_log(db: Session, serial_number: int, broker_password: str):
    db_device_log = models.DeviceLog(serial_number=serial_number, broker_password=broker_password)
    db.add(db_device_log)
    db.commit()
    db.refresh(db_device_log)
    return db_device_log

def remove_device_log(db: Session, serial_number: int):
    print(serial_number)
    return delete_item(db, get_device_log, serial_number)

def get_device_logs(db: Session):
    return db.query(models.Device).all()