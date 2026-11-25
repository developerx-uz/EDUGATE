from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from app.models.attendance import AttendanceEventType, AttendanceStatus


class AttendanceEventCreate(BaseModel):
    """Kameradan yoki Edge qurilmadan keluvchi hodisa formati."""
    student_id: Optional[str] = Field(None, description="Tizimdagi o'quvchi UUID si")
    student_code: Optional[str] = Field(None, description="O'quvchi kodi (SCH01-001)")
    rfid_card_id: Optional[str] = Field(None, description="Turniket karta kodi")
    event_type: AttendanceEventType = Field(AttendanceEventType.ENTRY, description="Kirish yoki Chiqish")
    event_time: Optional[datetime] = Field(None, description="Voqea sodir bo'lgan vaqt (ixtiyoriy)")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Yuz tanish aniqligi (0..1)")
    snapshot_base64: Optional[str] = Field(None, description="Kamera olgan kadr (ixtiyoriy)")


class AttendanceEventResponse(BaseModel):
    status: str
    message: str
    is_debounced: bool = False
    log_id: Optional[str] = None
    student_name: Optional[str] = None
    event_type: Optional[AttendanceEventType] = None
    event_time: Optional[datetime] = None
    attendance_status: Optional[AttendanceStatus] = None
    snapshot_path: Optional[str] = None


class AttendanceLogOut(BaseModel):
    id: str
    student_id: str
    student_name: str
    student_code: Optional[str] = None
    school_id: Optional[str] = None
    school_name: Optional[str] = None
    device_name: Optional[str] = None
    class_name: str
    event_type: AttendanceEventType
    status: AttendanceStatus
    event_time: datetime
    confidence: float
    snapshot_path: Optional[str] = None
    is_notified: bool

    model_config = ConfigDict(from_attributes=True)


class AbsenceReasonCreate(BaseModel):
    student_id: str
    reason: str = Field(..., min_length=2, max_length=1000)
    date: Optional[str] = None
    document_url: Optional[str] = None
    parent_chat_id: Optional[int] = None


class AbsenceStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(PENDING|APPROVED|REJECTED)$")


class AbsenceReasonOut(BaseModel):
    id: str
    student_id: str
    student_name: Optional[str] = None
    class_name: Optional[str] = None
    school_id: Optional[str] = None
    parent_id: Optional[str] = None
    reason: str
    absence_date: str
    document_url: Optional[str] = None
    status: str
    reviewed_by: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
