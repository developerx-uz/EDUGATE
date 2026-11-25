from dataclasses import dataclass
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.setting import SystemSetting


@dataclass
class EffectiveSettings:
    school_start_time: str
    late_threshold_minutes: int
    school_end_time: str
    debounce_minutes: int
    language: str
    admin_chat_id: Optional[str]
    notify_late: bool
    notify_entry: bool
    notify_exit: bool
    bot_token_configured: bool


async def get_effective_settings(
    db: AsyncSession, school_id: Optional[str] = None
) -> EffectiveSettings:
    """Resolve effective settings: school override -> global DB row -> env defaults."""
    global_row = (
        await db.execute(select(SystemSetting).filter(SystemSetting.school_id.is_(None)))
    ).scalar_one_or_none()

    school_row = None
    if school_id:
        school_row = (
            await db.execute(select(SystemSetting).filter(SystemSetting.school_id == school_id))
        ).scalar_one_or_none()

    row = school_row or global_row
    return EffectiveSettings(
        school_start_time=(row.school_start_time if row else None) or settings.SCHOOL_START_TIME,
        late_threshold_minutes=(
            row.late_threshold_minutes if (row and row.late_threshold_minutes is not None)
            else settings.LATE_THRESHOLD_MINUTES
        ),
        school_end_time=(row.school_end_time if row else None) or settings.SCHOOL_END_TIME,
        debounce_minutes=(
            row.debounce_minutes if (row and row.debounce_minutes is not None)
            else settings.DEBOUNCE_MINUTES
        ),
        language=(row.language if row else None) or "uz",
        admin_chat_id=(row.admin_chat_id if row else None) or (global_row.admin_chat_id if global_row else None) or settings.ADMIN_CHAT_ID,
        notify_late=row.notify_late if row is not None else True,
        notify_entry=row.notify_entry if row is not None else True,
        notify_exit=row.notify_exit if row is not None else False,
        bot_token_configured=bool(
            settings.TELEGRAM_BOT_TOKEN
            and ":" in settings.TELEGRAM_BOT_TOKEN
            and not settings.TELEGRAM_BOT_TOKEN.startswith("your_")
        ),
    )
