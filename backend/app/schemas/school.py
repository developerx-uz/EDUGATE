from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel


class SchoolCreate(BaseModel):
    name: str
    code: str
    address: Optional[str] = None
    phone: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None
    admin_username: Optional[str] = None
    admin_password: Optional[str] = None


class SchoolOut(BaseModel):
    id: str
    name: str
    code: str
    address: Optional[str] = None
    phone: Optional[str] = None
    settings: Dict[str, Any] = {}
    admin_username: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

