from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel


class SchoolCreate(BaseModel):
    name: str
    code: str
    address: Optional[str] = None
    phone: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None


class SchoolOut(BaseModel):
    id: str
    name: str
    code: str
    address: Optional[str]
    phone: Optional[str]
    settings: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True

