from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.models.attendance import AttendanceEventType, AttendanceStatus


class AttendanceEventCreate(BaseModel):
    """
    Kameradan yoki Edge qurilmadan keluvchi hodisa formati
    """
    student_id: Optional[str] = Field(None, description="Tizimdagi o'quvchi UUID si")
    student_code: Optional[str] = Field(None, description="O'quvchi kodi (SCH01-001) agar ID noma'lum bo'lsa")
    rfid_card_id: Optional[str] = Field(None, description="Turniket karta kodi")
    event_type: AttendanceEventType = Field(AttendanceEventType.ENTRY, description="Kirish yoki Chiqish")
    event_time: Optional[datetime] = Field(default_factory=datetime.utcnow, description="Voqea sodir bo'lgan vaqt")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Yuz tanish aniqligi foizi")
    snapshot_base64: Optional[str] = Field(None, description="Kamera o'sha soniyada olgan kadr (ixtiyoriy)")


class AttendanceEventResponse(BaseModel):
    status: str
    message: str
    is_debounced: bool = False
    log_id: Optional[str] = None
    student_name: Optional[str] = None
    event_type: Optional[AttendanceEventType] = None
    event_time: Optional[datetime] = None
    attendance_status: Optional[AttendanceStatus] = None


class AttendanceLogOut(BaseModel):
    id: str
    student_id: str
    student_name: str
    class_name: str
    event_type: AttendanceEventType
    status: AttendanceStatus
    event_time: datetime
    confidence: float
    is_notified: bool

    class Config:
        from_attributes = True

