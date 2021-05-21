from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    hashed_password = Column(String)

    user_houses = relationship("House", back_populates="owner")


class House(Base):
    __tablename__ = "houses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="user_houses")
    devices = relationship("Device", back_populates="house_devices")
    rules = relationship("Rule", back_populates="house_rules")
    house_schedules = relationship("Schedule", back_populates="schedule_houses")


class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    serial_number = Column(Integer, unique=True, index=True)
    name = Column(String)
    type = Column(String)
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
    condition = Column(String)
    house_id = Column(Integer, ForeignKey("houses.id"))
    device_sn = Column(Integer, ForeignKey("devices.id"))

    house_rules = relationship("House", back_populates="rules")
    device_devices = relationship("Device", back_populates="rule_devices")


class Schedule(Base):
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True)
    time_hours = Column(Integer)
    time_minutes = Column(Integer)
    value = Column(Integer)
    repeat = Column(String)

    house_id = Column(Integer, ForeignKey("houses.id"))
    device_id = Column(Integer, ForeignKey("devices.id"))

    schedule_devices = relationship("Device", back_populates="device_schedules")
    schedule_houses = relationship("House", back_populates="house_schedules")
