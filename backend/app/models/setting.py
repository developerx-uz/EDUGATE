import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base
from app.core.config import get_local_now, settings


class SystemSetting(Base):
    __tablename__ = "system_settings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    school_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("schools.id", ondelete="CASCADE"), nullable=True, unique=True, index=True
    )
    school_start_time: Mapped[str] = mapped_column(String(10), default=lambda: settings.SCHOOL_START_TIME)
    late_threshold_minutes: Mapped[int] = mapped_column(Integer, default=lambda: settings.LATE_THRESHOLD_MINUTES)
    school_end_time: Mapped[str] = mapped_column(String(10), default=lambda: settings.SCHOOL_END_TIME)
    debounce_minutes: Mapped[int] = mapped_column(Integer, default=lambda: settings.DEBOUNCE_MINUTES)
    language: Mapped[str] = mapped_column(String(10), default="uz")
    admin_chat_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    notify_late: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_entry: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_exit: Mapped[bool] = mapped_column(Boolean, default=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=get_local_now, onupdate=get_local_now)
