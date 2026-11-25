import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base
from app.core.config import get_local_now


class LeadOrder(Base):
    __tablename__ = "lead_orders"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    phone: Mapped[str] = mapped_column(String(50), nullable=False)
    region: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    school_info: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    students_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    recommended_turnstiles: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    recommended_cameras: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source: Mapped[str] = mapped_column(String(50), default="landing_contact")
    status: Mapped[str] = mapped_column(String(30), default="NEW", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_local_now, index=True)
