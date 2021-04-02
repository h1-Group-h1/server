from pydantic import BaseModel


# Standard JSON items
class DeviceId(BaseModel):
    id: int


class DeviceAction(BaseModel):
    id: str
    value: int


class RuleId(BaseModel):
    id: int


class ScheduleItem(BaseModel):
    time: str
    action: DeviceAction


class RequestResponse(BaseModel):
    status: int
    payload: str


# Database JSON items
class DeviceBase(BaseModel):
    house_id: int
    user_assigned_name: str
    serial_number: int


class DeviceCreate(DeviceBase):
    pass


class Device(DeviceBase):

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
    action: str  # DeviceAction.json()
    house_id: int


class RuleCreate(RuleBase):
    pass


class Rule(RuleBase):
    id: int

    class Config:
        orm_mode = True


class HouseBase(BaseModel):
    name: str
    owner_id: int


class HouseCreate(HouseBase):
    pass


class House(HouseBase):
    id: int

    class Config:
        orm_mode = True
