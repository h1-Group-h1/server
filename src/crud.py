from sqlalchemy.orm import Session

import models, schemas


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 0):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(email=user.email, name=user.name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_house(db: Session, house_id: int):
    return db.query(models.House).filter(models.House.id == house_id).first()

def get_houses(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.House).offset(skip).limit(limit).all()


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


def get_device(db: Session, id: int):
    return db.query(models.Device).filter(models.Device.id == id).first()


def get_device_by_sn(db: Session, device_sn: int):
    return db.query(models.Device).filter(models.Device.serial_number == device_sn).first()


def get_devices_by_house(db: Session, house_id: int):
    return db.query(models.Device).filter(models.Device.house_id == house_id).all()


def create_house_device(db: Session, device: schemas.DeviceCreate, house_id: int):
    db_device = models.Device(**device.dict(), house_id=house_id)
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    return db_device


# TODO: Update and delete

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
