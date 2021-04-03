from pydantic import BaseModel


# Standard JSON items
class DeviceId(BaseModel):
    id: int


class DeviceAction(BaseModel):
    id: int
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


class UserBase(BaseModel):
    email: str
    name: str


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: int

    class Config:
        orm_mode = True


class RuleBase(BaseModel):
    sensor_id: int
    device_id: int
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
