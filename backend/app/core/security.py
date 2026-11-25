import hmac
import secrets
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional
import bcrypt
from jose import jwt
from app.core.config import settings


def _prepare_bcrypt_secret(password: str) -> bytes:
    """Encode password safely within bcrypt's 72-byte limit without silent truncation."""
    raw = password.encode("utf-8")
    if len(raw) > 72:
        return hashlib.sha256(raw).hexdigest().encode("ascii")
    return raw


def get_password_hash(password: str) -> str:
    """Hash password with a random per-user bcrypt salt."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(_prepare_bcrypt_secret(password), salt).decode("utf-8")


def needs_password_rehash(hashed_password: str) -> bool:
    """Return True if the stored hash uses a legacy format and should be upgraded to bcrypt."""
    return not (hashed_password or "").startswith(("$2a$", "$2b$", "$2y$"))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against bcrypt hash or legacy salted SHA-256 hash."""
    if not hashed_password:
        return False
    if hashed_password.startswith(("$2a$", "$2b$", "$2y$")):
        try:
            return bcrypt.checkpw(
                _prepare_bcrypt_secret(plain_password),
                hashed_password.encode("utf-8")
            )
        except Exception:
            return False

    # Legacy SHA-256 fallback (for existing DB records prior to bcrypt upgrade)
    salted = f"{settings.SECRET_KEY}:{plain_password}"
    legacy_digest = hashlib.sha256(salted.encode("utf-8")).hexdigest()
    return hmac.compare_digest(legacy_digest, hashed_password)


def generate_device_token() -> str:
    """Kamera yoki turniketlar uchun xavfsiz API kalit generatsiya qiladi."""
    return f"edugate_dev_{secrets.token_urlsafe(32)}"


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
