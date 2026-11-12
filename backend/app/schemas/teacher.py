from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class TeacherCreate(BaseModel):
    school_id: str
    first_name: str
    last_name: str
    phone_number: Optional[str] = None
    subject: Optional[str] = None
    class_name: Optional[str] = None


class TeacherOut(BaseModel):
    id: str
    school_id: str
    first_name: str
    last_name: str
    full_name: str
    phone_number: Optional[str] = None
    subject: Optional[str] = None
    class_name: Optional[str] = None
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
