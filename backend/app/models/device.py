import uuid
import enum
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class DeviceDirection(str, enum.Enum):
    IN = "IN"          # Maktabga kirish
    OUT = "OUT"        # Maktabdan chiqish
    BIDIRECTIONAL = "BIDIRECTIONAL" # Ikkala tomonga


class DeviceType(str, enum.Enum):
    AI_CAMERA = "AI_CAMERA"      # Face ID kamera
    TURNSTILE = "TURNSTILE"      # Turniket / RFID o'quvchi
    EDGE_BOX = "EDGE_BOX"        # Mini PC / Jetson AI moduli
    MANUAL_APP = "MANUAL_APP"    # Navbatchi plansheti/telefoni


class Device(Base):
    __tablename__ = "devices"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    school_id: Mapped[str] = mapped_column(String(36), ForeignKey("schools.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False) # Masalan: "Bosh kirish - Kamera 1"
    device_token: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    device_type: Mapped[DeviceType] = mapped_column(SQLEnum(DeviceType), default=DeviceType.AI_CAMERA)
    direction: Mapped[DeviceDirection] = mapped_column(SQLEnum(DeviceDirection), default=DeviceDirection.IN)
    ip_address: Mapped[str] = mapped_column(String(45), nullable=True)
    location_description: Mapped[str] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_heartbeat: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Bog'lanishlar
    school = relationship("School", back_populates="devices")
    attendance_logs = relationship("AttendanceLog", back_populates="device")
