import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.core.config import get_local_now
from app.models.parent import student_parents


class Student(Base):
    __tablename__ = "students"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    school_id: Mapped[str] = mapped_column(String(36), ForeignKey("schools.id", ondelete="CASCADE"), nullable=False, index=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    student_code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    pinfl: Mapped[Optional[str]] = mapped_column(String(14), index=True, nullable=True)
    birth_cert_number: Mapped[Optional[str]] = mapped_column(String(50), index=True, nullable=True)
    gender: Mapped[Optional[str]] = mapped_column(String(1), nullable=True)  # "M" or "F"
    class_name: Mapped[str] = mapped_column(String(20), index=True, nullable=False)
    rfid_card_id: Mapped[Optional[str]] = mapped_column(String(50), index=True, nullable=True)
    face_encoding: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    photo_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_local_now)

    # Bog'lanishlar
    school = relationship("School", back_populates="students")
    parents = relationship("Parent", secondary=student_parents, back_populates="students")
    attendance_logs = relationship("AttendanceLog", back_populates="student", cascade="all, delete-orphan")
    absence_requests = relationship("AbsenceRequest", back_populates="student", cascade="all, delete-orphan")

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @property
    def inferred_gender(self) -> str:
        """Return explicit gender if set, otherwise infer from PINFL or surname."""
        if self.gender in ("M", "F"):
            return self.gender
        if self.pinfl and len(self.pinfl) >= 1 and self.pinfl[0] in ("4", "6"):
            return "F"
        if self.pinfl and len(self.pinfl) >= 1 and self.pinfl[0] in ("3", "5"):
            return "M"
        ln = (self.last_name or "").strip().lower()
        if ln.endswith(("va", "qizi", "yeva", "ova")):
            return "F"
        return "M"
