import html
import logging
from typing import List, Optional
import httpx
from sqlalchemy import select

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models.attendance import AttendanceLog

logger = logging.getLogger("edugate.notifier")


class TelegramNotifier:
    def __init__(self, token: Optional[str] = None):
        self.token = token

    def _get_token(self) -> Optional[str]:
        tok = self.token or settings.TELEGRAM_BOT_TOKEN
        if not tok or ":" not in tok or tok.startswith(("your_", "YOUR_")):
            return None
        return tok

    async def send_attendance_alert(
        self,
        chat_ids: List[int],
        student_name: str,
        event_type: str,
        event_time_str: str,
        is_late: bool = False,
        is_early_leave: bool = False,
        school_name: Optional[str] = None,
        log_id: Optional[str] = None,
    ) -> bool:
        """Ota-onaga Telegram orqali xabar yuborish va bazada is_notified belgilash."""
        token = self._get_token()
        if not token or not chat_ids:
            logger.info(
                f"[NOTIFIER SIMULATION] Ota-onaga xabar (Token yo'q): {student_name} - {event_type} - {event_time_str}"
            )
            return False

        safe_name = html.escape(student_name)
        safe_school = html.escape(school_name) if school_name else "EduGate Maktabi"
        safe_time = html.escape(event_time_str)

        if event_type == "ENTRY":
            action_text = "maktabga kirdi"
            status_emoji = "🟡" if is_late else "🟢"
            note = "\n⚠️ <b>Eslatma:</b> Darsga biroz kechikib keldi." if is_late else ""
        else:
            action_text = "maktabdan chiqdi"
            status_emoji = "🟠" if is_early_leave else "🔴"
            note = "\n⚠️ <b>Eslatma:</b> Dars tugashidan oldin maktabdan chiqdi." if is_early_leave else ""

        text = (
            f"{status_emoji} <b>EDUGATE Xabarnomasi</b>\n\n"
            f"Hurmatli ota-ona!\n"
            f"Farzandingiz <b>{safe_name}</b> soat <b>{safe_time}</b> da {action_text}.{note}\n\n"
            f"🏫 <i>{safe_school}</i>"
        )

        api_url = f"https://api.telegram.org/bot{token}/sendMessage"
        sent_any = False

        async with httpx.AsyncClient(timeout=5.0) as client:
            for chat_id in chat_ids:
                try:
                    resp = await client.post(
                        api_url,
                        json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"},
                    )
                    if resp.status_code == 200:
                        sent_any = True
                    else:
                        logger.warning(f"Telegram API {resp.status_code} (chat_id={chat_id}): {resp.text}")
                except Exception as e:
                    logger.error(f"Telegram xabar yuborishda xatolik (chat_id: {chat_id}): {e}")

        if sent_any and log_id:
            try:
                async with AsyncSessionLocal() as session:
                    res = await session.execute(select(AttendanceLog).filter(AttendanceLog.id == log_id))
                    log = res.scalar_one_or_none()
                    if log:
                        log.is_notified = True
                        await session.commit()
            except Exception as e:
                logger.warning(f"is_notified yangilanishida xatolik: {e}")

        return sent_any

    async def send_admin_alert(self, text: str, chat_id: Optional[str] = None) -> bool:
        """Send operational/lead alerts to configured admin Telegram chat."""
        token = self._get_token()
        target_chat = chat_id or settings.ADMIN_CHAT_ID
        if not token or not target_chat:
            return False

        api_url = f"https://api.telegram.org/bot{token}/sendMessage"
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.post(
                    api_url,
                    json={"chat_id": target_chat, "text": text, "parse_mode": "HTML"},
                )
                return resp.status_code == 200
        except Exception as e:
            logger.warning(f"Admin Telegram alert error: {e}")
            return False


notifier = TelegramNotifier()
