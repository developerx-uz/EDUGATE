import httpx
import logging
from typing import Optional, Dict, Any, List
from bot.config import settings

logger = logging.getLogger("EdugateBot.API")

class EdugateAPIClient:
    def __init__(self, base_url: str = settings.CORE_API_URL):
        self.base_url = base_url.rstrip("/")

    async def link_parent(self, phone: str, chat_id: int, full_name: str, username: Optional[str] = None) -> Dict[str, Any]:
        """Ota-onani telefon raqami va chat_id orqali tizimga bog'lash"""
        url = f"{self.base_url}/parents/link"
        payload = {
            "phone_number": phone,
            "telegram_chat_id": str(chat_id),
            "full_name": full_name,
            "username": username
        }
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(url, json=payload)
                if res.status_code in [200, 201]:
                    return res.json()
                logger.warning(f"Parent link failed: status {res.status_code}")
                return {"success": False, "message": "Backend aloqada xatolik"}
        except Exception as e:
            logger.error(f"Error calling {url}: {e}")
            return {"success": False, "error": str(e)}

    async def get_children(self, chat_id: int) -> List[Dict[str, Any]]:
        """Ota-onaga biriktirilgan barcha o'quvchilarni olish"""
        url = f"{self.base_url}/parents/{chat_id}/children"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.get(url)
                if res.status_code == 200:
                    return res.json()
                return []
        except Exception as e:
            logger.error(f"Error fetching children: {e}")
            return []

    async def get_today_attendance(self, student_id: int) -> Optional[Dict[str, Any]]:
        """O'quvchining bugungi keldi-ketdi holatini olish"""
        url = f"{self.base_url}/attendance/student/{student_id}/today"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.get(url)
                if res.status_code == 200:
                    return res.json()
                return None
        except Exception as e:
            logger.error(f"Error fetching attendance: {e}")
            return None

    async def submit_absence_reason(self, student_id: int, reason: str, date: str, document_url: Optional[str] = None) -> bool:
        """Sababli dars qoldirish haqida xat/ariza yuborish"""
        url = f"{self.base_url}/attendance/absence-reason"
        payload = {
            "student_id": student_id,
            "reason": reason,
            "date": date,
            "document_url": document_url
        }
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(url, json=payload)
                return res.status_code in [200, 201]
        except Exception as e:
            logger.error(f"Error submitting absence reason: {e}")
            return False

    async def submit_school_order(self, data: Dict[str, Any]) -> bool:
        """Saytdan yoki botdan yangi turniket/kamera buyurtmasini qabul qilish"""
        url = f"{self.base_url}/orders/new"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(url, json=data)
                return res.status_code in [200, 201]
        except Exception as e:
            logger.error(f"Error submitting order: {e}")
            return False

api_client = EdugateAPIClient()

