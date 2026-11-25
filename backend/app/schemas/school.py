from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict


class SchoolCreate(BaseModel):
    name: str
    code: str
    address: Optional[str] = None
    phone: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None
    admin_username: Optional[str] = None
    admin_password: Optional[str] = None


class SchoolUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None


class SchoolOut(BaseModel):
    id: str
    name: str
    code: str
    address: Optional[str] = None
    phone: Optional[str] = None
    settings: Dict[str, Any] = {}
    admin_username: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
