from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)

    user_houses = relationship("House", back_populates="owner")


class House(Base):
    __tablename__ = "houses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="user_houses")
    devices = relationship("Device", back_populates="house_devices")
    rules = relationship("Rule", back_populates="house_rules")


class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    serial_number = Column(Integer, unique=True, index=True)
    name = Column(String)
    house_id = Column(Integer, ForeignKey("houses.id"))

    house_devices = relationship("House", back_populates="devices")


class Rule(Base):
    __tablename__ = "rules"

    id = Column(Integer, primary_key=True, index=True)
    action = Column(String)
    activate_value = Column(Integer)
    condition = Column(String)
    house_id = Column(Integer, ForeignKey("houses.id"))

    house_rules = relationship("House", back_populates="rules")
