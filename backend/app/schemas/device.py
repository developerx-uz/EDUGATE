from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.models.device import DeviceDirection, DeviceType


class DeviceCreate(BaseModel):
    school_id: Optional[str] = None
    name: str
    device_type: DeviceType = DeviceType.AI_CAMERA
    direction: DeviceDirection = DeviceDirection.IN
    ip_address: Optional[str] = None
    location_description: Optional[str] = None


class DeviceUpdate(BaseModel):
    name: Optional[str] = None
    device_type: Optional[DeviceType] = None
    direction: Optional[DeviceDirection] = None
    ip_address: Optional[str] = None
    location_description: Optional[str] = None
    is_active: Optional[bool] = None


class DeviceHeartbeatRequest(BaseModel):
    ip_address: Optional[str] = None


class DeviceOut(BaseModel):
    id: str
    school_id: str
    school_name: Optional[str] = None
    name: str
    device_token: str
    device_type: DeviceType
    direction: DeviceDirection
    ip_address: Optional[str] = None
    location_description: Optional[str] = None
    is_active: bool
    is_online: bool = False
    last_heartbeat: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
