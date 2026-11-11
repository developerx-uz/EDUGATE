from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class StudentCreate(BaseModel):
    school_id: str
    first_name: str
    last_name: str
    student_code: str
    class_name: str
    rfid_card_id: Optional[str] = None
    face_encoding: Optional[str] = None


class StudentOut(BaseModel):
    id: str
    school_id: str
    first_name: str
    last_name: str
    student_code: str
    class_name: str
    rfid_card_id: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
