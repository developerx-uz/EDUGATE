from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class ParentLinkRequest(BaseModel):
    phone_number: str = Field(..., min_length=7, max_length=30)
    telegram_chat_id: int
    full_name: Optional[str] = None
    username: Optional[str] = None


class ParentLinkStudentRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=200)
    phone_number: str = Field(..., min_length=7, max_length=30)
    student_id: str
    relationship_type: str = "OTA_ONA"


class ParentOut(BaseModel):
    id: str
    full_name: str
    phone_number: str
    telegram_chat_id: Optional[int] = None
    is_verified: bool
    students: List[str] = []
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LeadOrderCreate(BaseModel):
    full_name: Optional[str] = None
    contact_name: Optional[str] = None
    phone: Optional[str] = None
    phone_number: Optional[str] = None
    region: Optional[str] = None
    school_info: Optional[str] = None
    school_name: Optional[str] = None
    students_count: Optional[int] = None
    message: Optional[str] = None
    source: str = "landing_contact"


class LeadOrderStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(NEW|CONTACTED|COMPLETED)$")


class LeadOrderOut(BaseModel):
    id: str
    full_name: str
    phone: str
    region: Optional[str] = None
    school_info: Optional[str] = None
    students_count: Optional[int] = None
    recommended_turnstiles: Optional[int] = None
    recommended_cameras: Optional[int] = None
    message: Optional[str] = None
    source: str
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SystemSettingsOut(BaseModel):
    school_start_time: str = "08:00"
    late_threshold_minutes: int = 15
    school_end_time: str = "14:00"
    debounce_minutes: int = 15
    language: str = "uz"
    admin_chat_id: Optional[str] = None
    notify_late: bool = True
    notify_entry: bool = True
    notify_exit: bool = False
    bot_token_configured: bool = False


class SystemSettingsUpdate(BaseModel):
    school_start_time: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$")
    late_threshold_minutes: Optional[int] = Field(None, ge=0, le=180)
    school_end_time: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$")
    debounce_minutes: Optional[int] = Field(None, ge=1, le=120)
    language: Optional[str] = Field(None, pattern="^(uz|ru|en|kz|kg)$")
    admin_chat_id: Optional[str] = None
    notify_late: Optional[bool] = None
    notify_entry: Optional[bool] = None
    notify_exit: Optional[bool] = None
