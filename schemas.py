from pydantic import BaseModel
from datetime import date
from typing import Optional, List
from db.models.devices import DeviceTypeEnum, InitialStateEnum, OperationalStatusEnum, ConnectionStatusEnum, SoftwareVersionEnum

class ComponentCreate(BaseModel):
    type: str

class DeviceCreateBase(BaseModel):
    serial_number: int
    type: DeviceTypeEnum
    software_version: SoftwareVersionEnum
    image: str
    initial_state: InitialStateEnum
    mac_address: str
    operational_status: OperationalStatusEnum
    connection_status: ConnectionStatusEnum
    battery_level: int
    creation_date: date
    user_id: Optional[int] = None
    components: Optional[List[ComponentCreate]] = []


class DeviceUpdateBase(BaseModel):
    type: DeviceTypeEnum
    software_version: str
    image: str
    initial_state: InitialStateEnum
    mac_address: str
    operational_status: OperationalStatusEnum
    connection_status: ConnectionStatusEnum
    battery_level: int
    user_id: Optional[int] = None
    components: Optional[List[ComponentCreate]] = []
