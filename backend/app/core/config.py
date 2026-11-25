from datetime import datetime, timedelta, timezone
from typing import Optional, Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "EDUGATE Attendance System"
    VERSION: str = "1.1.0"
    DEBUG: bool = True

    @field_validator("DEBUG", mode="before")
    @classmethod
    def parse_debug(cls, v: Any) -> bool:
        if isinstance(v, str):
            if v.lower() in ("true", "1", "yes", "on", "t"):
                return True
            if v.lower() in ("false", "0", "no", "off", "f", "release", "prod", "production"):
                return False
        return bool(v)

    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "edugate-super-secret-key-production-ready-32-chars-min"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # Boshlang'ich hisob parollari (.env orqali almashtirish mumkin)
    INITIAL_ADMIN_PASSWORD: str = "Daminol007$"
    INITIAL_MINISTRY_PASSWORD: str = "XalqTalimi2026!"

    # Ma'lumotlar bazasi
    USE_SQLITE: bool = True
    SQLITE_DB_PATH: str = "./edugate_local.db"
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "edugate_db"
    POSTGRES_PORT: int = 5432
    DATABASE_URL: Optional[str] = None

    # Redis & Qurilmalar
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    DEBOUNCE_MINUTES: int = 15
    DEVICE_OFFLINE_SECONDS: int = 300

    # Maktab vaqtlari va mintaqaviy vaqt (Asia/Tashkent UTC+5)
    TIMEZONE: str = "Asia/Tashkent"
    SCHOOL_START_TIME: str = "08:00"
    SCHOOL_END_TIME: str = "14:00"
    LATE_THRESHOLD_MINUTES: int = 15

    # Telegram Bot
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    ADMIN_CHAT_ID: Optional[str] = None
    BOT_API_SECRET: Optional[str] = None

    # Davlat va e-Maktab API Sozlamalari
    EMAKTAB_API_URL: str = "https://api.emaktab.uz/v1"
    EMAKTAB_API_TOKEN: Optional[str] = None
    EGOV_API_URL: str = "https://my.gov.uz/api/v1"
    EGOV_API_TOKEN: Optional[str] = None

    @property
    def async_database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        if self.USE_SQLITE:
            return f"sqlite+aiosqlite:///{self.SQLITE_DB_PATH}"
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow"
    )


settings = Settings()


def get_local_tz():
    """Return configured school timezone, falling back to UTC+5 (Tashkent) if tzdata is absent."""
    try:
        return ZoneInfo(settings.TIMEZONE)
    except ZoneInfoNotFoundError:
        return timezone(timedelta(hours=5))


def get_local_now() -> datetime:
    """Return current naive datetime in the configured local school timezone."""
    return datetime.now(get_local_tz()).replace(tzinfo=None)


def to_local_naive(dt: Optional[datetime]) -> datetime:
    """Normalize an incoming datetime (aware or naive) to naive local school time."""
    if dt is None:
        return get_local_now()
    if dt.tzinfo is not None:
        return dt.astimezone(get_local_tz()).replace(tzinfo=None)
    return dt
