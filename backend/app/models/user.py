import uuid
import enum
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class UserRole(str, enum.Enum):
    SUPERADMIN = "SUPERADMIN"             # Sayt & Server / DevOps ma'murlari (/admin)
    MINISTRY_VIEWER = "MINISTRY_VIEWER"   # Xalq Ta'limi / MMTV / Hokimlik (Faqat ko'rish - Read-Only)
    SCHOOL_ADMIN = "SCHOOL_ADMIN"         # Maktab boshqaruvi (1 maktab = 1 login)


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    school_id: Mapped[str] = mapped_column(String(36), ForeignKey("schools.id", ondelete="SET NULL"), nullable=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=True)
    full_name: Mapped[str] = mapped_column(String(100), nullable=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(SQLEnum(UserRole, native_enum=False), default=UserRole.SUPERADMIN)
    is_superadmin: Mapped[bool] = mapped_column(Boolean, default=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now().replace(tzinfo=None))

    school = relationship("School", back_populates="admin_user")
