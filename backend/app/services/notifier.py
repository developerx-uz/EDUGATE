import httpx
import logging
from typing import List, Optional
from app.core.config import settings

logger = logging.getLogger("edugate.notifier")


class TelegramNotifier:
    def __init__(self, token: Optional[str] = None):
        self.token = token or settings.TELEGRAM_BOT_TOKEN
        self.api_url = f"https://api.telegram.org/bot{self.token}/sendMessage" if self.token else None

    async def send_attendance_alert(
        self,
        chat_ids: List[int],
        student_name: str,
        event_type: str,
        event_time_str: str,
        is_late: bool = False
    ):
        """Ota-onaga Telegram orqali xabar yuborish"""
        if not self.token or not chat_ids:
            logger.info(f"[NOTIFIER SIMULATION] Ota-onaga xabar (Token yo'q): {student_name} - {event_type} - {event_time_str}")
            return

        status_emoji = "🚪"
        if event_type == "ENTRY":
            action_text = "maktabga kirdi"
            status_emoji = "🟢" if not is_late else "🟡"
            late_note = "\n⚠️ *Eslatma:* Darsga biroz kechikib keldi." if is_late else ""
        else:
            action_text = "maktabdan chiqdi"
            status_emoji = "🔴"
            late_note = ""

        text = (
            f"{status_emoji} *EDUGATE Xabarnomasi*\n\n"
            f"Hurmatli ota-ona!\n"
            f"Farzandingiz *{student_name}* soat *{event_time_str}* da {action_text}.{late_note}\n\n"
            f"📍 _Tizim: EduGate Xavfsizlik Portali_"
        )

        async with httpx.AsyncClient(timeout=5.0) as client:
            for chat_id in chat_ids:
                try:
                    payload = {
                        "chat_id": chat_id,
                        "text": text,
                        "parse_mode": "Markdown"
                    }
                    await client.post(self.api_url, json=payload)
                except Exception as e:
                    logger.error(f"Telegram xabar yuborishda xatolik (chat_id: {chat_id}): {e}")


notifier = TelegramNotifier()

