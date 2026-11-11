from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.models.device import DeviceDirection, DeviceType


class DeviceCreate(BaseModel):
    school_id: str
    name: str
    device_type: DeviceType = DeviceType.AI_CAMERA
    direction: DeviceDirection = DeviceDirection.IN
    ip_address: Optional[str] = None
    location_description: Optional[str] = None


class DeviceOut(BaseModel):
    id: str
    school_id: str
    name: str
    device_token: str
    device_type: DeviceType
    direction: DeviceDirection
    ip_address: Optional[str]
    is_active: bool
    last_heartbeat: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True
