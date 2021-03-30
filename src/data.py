from pydantic import BaseModel
from typing import Optional


class Device(BaseModel):
    house_id: int
    serial_number: int
    user_assigned_name: Optional[str] = None
    device_id: Optional[str] = None


class User(BaseModel):
    email: str


class DeviceId(BaseModel):
    id: str


class DeviceAction(BaseModel):
    id: str
    value: int


class DeviceRule(BaseModel):
    id: int
    device_id: str
    value: int
    condition: str
    action: DeviceAction


class RuleId(BaseModel):
    id: int


class ScheduleItem(BaseModel):
    time: str
    action: DeviceAction


class NewHouse(BaseModel):
    user_id: int
    name: str


class ExistingHouse(BaseModel):
    user_id: int
    house_id: int
