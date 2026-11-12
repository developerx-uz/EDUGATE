from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class StudentCreate(BaseModel):
    school_id: str
    first_name: str
    last_name: str
    student_code: str
    class_name: str
    pinfl: Optional[str] = None
    birth_cert_number: Optional[str] = None
    rfid_card_id: Optional[str] = None
    face_encoding: Optional[str] = None
    photo_path: Optional[str] = None


class StudentOut(BaseModel):
    id: str
    school_id: str
    first_name: str
    last_name: str
    student_code: str
    class_name: str
    pinfl: Optional[str] = None
    birth_cert_number: Optional[str] = None
    rfid_card_id: Optional[str] = None
    face_encoding: Optional[str] = None
    photo_path: Optional[str] = None
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
