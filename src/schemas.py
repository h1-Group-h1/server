from sqlalchemy.sql.expression import intersect_all
from pydantic import BaseModel


# Standard JSON items
class DeviceId(BaseModel):
    id: int


class DeviceAction(BaseModel):
    serial_number: int
    value: int


class RuleId(BaseModel):
    id: int


class ScheduleItem(BaseModel):
    time_hours: int
    time_minutes: int
    action: DeviceAction


class RequestResponse(BaseModel):
    status: int
    payload: str


# Database JSON items
class DeviceBase(BaseModel):
    name: str
    serial_number: int
    type: str


class DeviceCreate(DeviceBase):
    pass


class Device(DeviceBase):
    id: int
    house_id: int

    class Config:
        orm_mode = True


class ScheduleBase(BaseModel):
    time_hours: int
    time_minutes: int
    device_id: int
    value: int
    repeat: str


class ScheduleCreate(ScheduleBase):
    pass


class Schedule(ScheduleBase):
    house_id: int
    id: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    email: str
    name: str
    password: str

class UserResponseBase(BaseModel):
    id: int

class UserResponse(UserResponseBase):
    email: str
    name: str

class UserCreate(UserBase):
    pass


class UserResponse(BaseModel):
    email: str
    name: str


class User(UserBase):
    id: int

    class Config:
        orm_mode = True


class RuleBase(BaseModel):
    sensor_sn: int
    device_sn: int
    value: int
    activation_value: int
    condition: str


class RuleCreate(RuleBase):
    pass


class Rule(RuleBase):
    house_id: int
    id: int

    class Config:
        orm_mode = True


class HouseBase(BaseModel):
    name: str


class HouseCreate(HouseBase):
    pass


class House(HouseBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True


class DeviceStatus(BaseModel):
    status: str


class CommandBase(BaseModel):
    type: str


class OperationCommand(CommandBase):
    type = "op"
    val: int


class AddRuleCommand(CommandBase):
    type = "ar"
    condition: str
    raw_value: int
    rule_id: int


class DelRuleCommand(CommandBase):
    type = "dr"
    rule_id: int


class AddScheduleCommand(CommandBase):
    type = "as"
    value: int
    th: int
    tm: int
    schedule_id: int
    repeat: str


class DelScheduleCommand(CommandBase):
    type = "ds"
    schedule_id: int
