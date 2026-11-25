import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class BotSettings(BaseSettings):
    BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN")
    CORE_API_URL: str = os.getenv("CORE_API_URL", "http://edugate_backend:8000/api/v1")
    ADMIN_CHAT_ID: str = os.getenv("ADMIN_CHAT_ID", "")
    CHANNEL_LOG_ID: str = os.getenv("CHANNEL_LOG_ID", "")
    BOT_API_SECRET: str = os.getenv("BOT_API_SECRET", "")
    WEBHOOK_MODE: bool = False

    @property
    def is_valid_token(self) -> bool:
        return bool(
            self.BOT_TOKEN
            and ":" in self.BOT_TOKEN
            and not self.BOT_TOKEN.startswith(("YOUR_", "your_"))
        )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = BotSettings()
