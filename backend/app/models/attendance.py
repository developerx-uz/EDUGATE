import uuid
import enum
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, Float, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class AttendanceEventType(str, enum.Enum):
    ENTRY = "ENTRY"      # Maktabga kirish
    EXIT = "EXIT"        # Maktabdan chiqish


class AttendanceStatus(str, enum.Enum):
    ON_TIME = "ON_TIME"  # O'z vaqtida kelgan
    LATE = "LATE"        # Kechikib kelgan
    EARLY_LEAVE = "EARLY_LEAVE" # Dars tugamasdan ketgan


class AttendanceLog(Base):
    __tablename__ = "attendance_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id: Mapped[str] = mapped_column(String(36), ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    device_id: Mapped[str] = mapped_column(String(36), ForeignKey("devices.id", ondelete="SET NULL"), nullable=True, index=True)
    event_type: Mapped[AttendanceEventType] = mapped_column(SQLEnum(AttendanceEventType), nullable=False)
    status: Mapped[AttendanceStatus] = mapped_column(SQLEnum(AttendanceStatus), default=AttendanceStatus.ON_TIME)
    confidence: Mapped[float] = mapped_column(Float, default=1.0) # Yuz tanish aniqligi (0.0 - 1.0)
    event_time: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    snapshot_path: Mapped[str] = mapped_column(String(500), nullable=True) # O'quvchi o'tgan paytdagi kadr fotosurati
    is_notified: Mapped[bool] = mapped_column(Boolean, default=False)

    # Bog'lanishlar
    student = relationship("Student", back_populates="attendance_logs")
    device = relationship("Device", back_populates="attendance_logs")
