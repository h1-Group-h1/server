from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(32), unique=True, index=True)
    name = Column(String(32))
    password = Column(String(256))
    broker_username = Column(String(32))
    broker_password = Column(String(256))

    user_houses = relationship("House", back_populates="owner")


class House(Base):
    __tablename__ = "houses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(32), index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="user_houses")
    devices = relationship("Device", back_populates="house_devices")
    rules = relationship("Rule", back_populates="house_rules")
    house_schedules = relationship("Schedule", back_populates="schedule_houses")


class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    serial_number = Column(Integer, unique=True, index=True)
    name = Column(String(32))
    type = Column(String(32))
    house_id = Column(Integer, ForeignKey("houses.id"))

    house_devices = relationship("House", back_populates="devices")
    rule_devices = relationship("Rule", back_populates="device_devices")
    device_schedules = relationship("Schedule", back_populates="schedule_devices")


class Rule(Base):
    __tablename__ = "rules"

    id = Column(Integer, primary_key=True, index=True)
    sensor_sn = Column(Integer)
    value = Column(Integer)
    activation_value = Column(Integer)
    condition = Column(String(32))
    house_id = Column(Integer, ForeignKey("houses.id"))
    device_sn = Column(Integer, ForeignKey("devices.serial_number"))

    house_rules = relationship("House", back_populates="rules")
    device_devices = relationship("Device", back_populates="rule_devices")


class Schedule(Base):
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True)
    time_hours = Column(Integer)
    time_minutes = Column(Integer)
    value = Column(Integer)
    repeat = Column(String(32))

    house_id = Column(Integer, ForeignKey("houses.id"))
    device_id = Column(Integer, ForeignKey("devices.id"))

    schedule_devices = relationship("Device", back_populates="device_schedules")
    schedule_houses = relationship("House", back_populates="house_schedules")

"""
class BrokerUser(Base):
    __tablename__ = "broker_users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(32))
    password = Column(String(32))
    user_id = Column(Integer, ForeignKey("users.id"))
    users = relationship("User", back_populates="users")

class BrokerAcl(Base):
    __tablename__ = "broker_acl"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(32))
    topic = Column(String(32))
    rw = Column(Integer)
"""