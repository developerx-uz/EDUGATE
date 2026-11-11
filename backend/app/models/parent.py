import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, BigInteger, Table, Column, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

student_parents = Table(
    "student_parents",
    Base.metadata,
    Column("student_id", String(36), ForeignKey("students.id", ondelete="CASCADE"), primary_key=True),
    Column("parent_id", String(36), ForeignKey("parents.id", ondelete="CASCADE"), primary_key=True),
    Column("relationship_type", String(50), default="OTA_ONA") # OTA, ONA, VASIY
)


class Parent(Base):
    __tablename__ = "parents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    telegram_chat_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True, nullable=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    students = relationship("Student", secondary=student_parents, back_populates="parents")

