from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "EDUGATE Attendance System"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "edugate-super-secret-key-production-ready-32-chars-min"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # Ma'lumotlar bazasi
    USE_SQLITE: bool = True
    SQLITE_DB_PATH: str = "./edugate_local.db"
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "edugate_db"
    POSTGRES_PORT: int = 5432
    DATABASE_URL: Optional[str] = None

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    DEBOUNCE_MINUTES: int = 15

    # Maktab vaqtlari
    SCHOOL_START_TIME: str = "08:00"
    LATE_THRESHOLD_MINUTES: int = 15

    # Telegram Bot
    TELEGRAM_BOT_TOKEN: Optional[str] = None

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

