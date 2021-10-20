from sqlalchemy.orm import  Session
from . import models
from .database import  SessionLocal, engine

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def add_device(serial_number: int, password: str):
    db = next(get_db())
    device_user = models.User(username=str(serial_number), password=password)
    db.add(device_user)
    db.commit()
    db.refresh(device_user)

    device_ACL_sub = models.ACL(topic=f"devices/{serial_number}", username=str(serial_number), user_id=device_user.id, rw=1)

    device_ACL_pub = models.ACL(topic=f"status/{serial_number}", username=str(serial_number), user_id=device_user.id, rw=2)
    db.add(device_ACL_sub)
    db.add(device_ACL_pub)
    db.commit()
    db.refresh(device_ACL_sub)
    db.refresh(device_ACL_pub)
    return device_user


# For now - use same username and password (hashed password)
def add_user(username: str, password: str):
    db = next(get_db())
    db_user = models.User(username=username, password=password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def add_device_to_user(serial_number: int, username: str):
    db = next(get_db())
    db_user = db.query(models.User).filter(models.User.username == username).first()
    user_acl_sub = models.ACL(topic=f"status/{serial_number}", username=username, user_id=db_user.id, rw=1)
    db.add(user_acl_sub)
    db.commit()
    db.refresh(user_acl_sub)
    return user_acl_sub


def add_server():
    db = next(get_db())
    db_server = models.User(username="server_admin", password="r3qg23JHIiubgqioj12bd290cbIGBUIGB", super=1)
    db.add(db_server)
    db.commit()
    db.refresh(db_server)
    return db_server
