import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.parent import student_parents


class Student(Base):
    __tablename__ = "students"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    school_id: Mapped[str] = mapped_column(String(36), ForeignKey("schools.id", ondelete="CASCADE"), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    student_code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False) # Masalan: "SCH01-2024-001"
    class_name: Mapped[str] = mapped_column(String(20), index=True, nullable=False) # Masalan: "7-A"
    rfid_card_id: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=True) # Turniket karta ID
    face_encoding: Mapped[str] = mapped_column(Text, nullable=True) # 128 yoki 512 o'lchamli AI yuz vektori (JSON/Base64)
    photo_path: Mapped[str] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Bog'lanishlar
    school = relationship("School", back_populates="students")
    parents = relationship("Parent", secondary=student_parents, back_populates="students")
    attendance_logs = relationship("AttendanceLog", back_populates="student", cascade="all, delete-orphan")

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
