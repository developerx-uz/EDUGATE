import httpx
import logging
from typing import Optional, Dict, Any, List
from bot.config import settings

logger = logging.getLogger("EdugateBot.API")


class EdugateAPIClient:
    def __init__(self, base_url: str = settings.CORE_API_URL):
        self.base_url = base_url.rstrip("/")

    def _headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if settings.BOT_API_SECRET:
            headers["X-Bot-Secret"] = settings.BOT_API_SECRET
        return headers

    async def _request(self, method: str, path: str, **kwargs) -> Optional[httpx.Response]:
        url = f"{self.base_url}{path}"
        headers = self._headers()
        if "headers" in kwargs:
            headers.update(kwargs.pop("headers"))
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                return await client.request(method, url, headers=headers, **kwargs)
        except Exception as e:
            logger.error(f"Error calling {method} {url}: {e}")
            return None

    async def link_parent(
        self, phone: str, chat_id: int, full_name: str, username: Optional[str] = None
    ) -> Dict[str, Any]:
        """Ota-onani telefon raqami va chat_id orqali tizimga bog'lash."""
        payload = {
            "phone_number": phone,
            "telegram_chat_id": chat_id,
            "full_name": full_name,
            "username": username,
        }
        res = await self._request("POST", "/parents/link", json=payload)
        if res and res.status_code in (200, 201):
            return res.json()
        logger.warning(f"Parent link failed: status {res.status_code if res else 'no-response'}")
        return {"success": False, "message": "Backend aloqada xatolik"}

    async def get_children(self, chat_id: int) -> List[Dict[str, Any]]:
        """Ota-onaga biriktirilgan barcha o'quvchilarni olish."""
        res = await self._request("GET", f"/parents/{chat_id}/children")
        if res and res.status_code == 200:
            return res.json()
        return []

    async def get_monthly_report(self, chat_id: int) -> Optional[Dict[str, Any]]:
        """Joriy oylik davomat hisobotini olish."""
        res = await self._request("GET", f"/parents/{chat_id}/monthly-report")
        if res and res.status_code == 200:
            return res.json()
        return None

    async def get_school_info(self, chat_id: int) -> Optional[Dict[str, Any]]:
        """Farzand o'qiydigan maktab va sinf rahbari ma'lumotlarini olish."""
        res = await self._request("GET", f"/parents/{chat_id}/school-info")
        if res and res.status_code == 200:
            return res.json()
        return None

    async def get_today_attendance(self, student_id: str) -> Optional[Dict[str, Any]]:
        """O'quvchining bugungi keldi-ketdi holatini olish."""
        res = await self._request("GET", f"/attendance/student/{student_id}/today")
        if res and res.status_code == 200:
            return res.json()
        return None

    async def submit_absence_reason(
        self,
        student_id: str,
        reason: str,
        date_str: str,
        parent_chat_id: Optional[int] = None,
        document_url: Optional[str] = None,
    ) -> bool:
        """Sababli dars qoldirish haqida xat/ariza yuborish."""
        payload = {
            "student_id": student_id,
            "reason": reason,
            "date": date_str,
            "parent_chat_id": parent_chat_id,
            "document_url": document_url,
        }
        res = await self._request("POST", "/attendance/absence-reason", json=payload)
        return bool(res and res.status_code in (200, 201))

    async def submit_school_order(self, data: Dict[str, Any]) -> bool:
        """Saytdan yoki botdan yangi turniket/kamera buyurtmasini saqlash."""
        res = await self._request("POST", "/orders/new", json=data)
        return bool(res and res.status_code in (200, 201))


api_client = EdugateAPIClient()
