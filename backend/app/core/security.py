import secrets
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import jwt
from app.core.config import settings


def get_password_hash(password: str) -> str:
    """Xavfsiz va barqaror parol xeshlash (SHA-256 + Salt)"""
    salted = f"{settings.SECRET_KEY}:{password}"
    return hashlib.sha256(salted.encode()).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Parolni tekshirish"""
    return get_password_hash(plain_password) == hashed_password


def generate_device_token() -> str:
    """Kamera yoki turniketlar uchun xavfsiz 64-belgili API kalit generatsiya qiladi"""
    return f"edugate_dev_{secrets.token_urlsafe(32)}"


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt
