import time
from typing import Optional
from app.core.config import settings

try:
    import redis.asyncio as aioredis
    HAS_REDIS = True
except ImportError:
    HAS_REDIS = False


class InMemoryDebounceCache:
    """Redis yo'q bo'lsa yoki lokal sinovda ishlaydigan xotira kesh mexanizmi"""
    def __init__(self):
        self._cache = {}

    async def get(self, key: str) -> Optional[str]:
        now = time.time()
        val = self._cache.get(key)
        if not val:
            return None
        expires_at, data = val
        if now > expires_at:
            del self._cache[key]
            return None
        return data

    async def set(self, key: str, value: str, ex: int = 900) -> bool:
        self._cache[key] = (time.time() + ex, value)
        return True


class DebounceManager:
    def __init__(self):
        self.redis_client = None
        self.fallback = InMemoryDebounceCache()

    async def initialize(self):
        if HAS_REDIS:
            try:
                self.redis_client = aioredis.Redis(
                    host=settings.REDIS_HOST,
                    port=settings.REDIS_PORT,
                    db=settings.REDIS_DB,
                    decode_responses=True
                )
                await self.redis_client.ping()
            except Exception:
                self.redis_client = None

    async def is_debounced(self, student_id: str, direction: str) -> bool:
        """
        Anti-passback & Debounce:
        O'quvchi oxirgi DEBOUNCE_MINUTES ichida ayni shu eshikdan/yo'nalishdan
        qayd etilgan bo'lsa True qaytaradi (spam hisoblanadi).
        """
        key = f"debounce:{student_id}:{direction}"
        if self.redis_client:
            try:
                val = await self.redis_client.get(key)
                return val is not None
            except Exception:
                pass
        return (await self.fallback.get(key)) is not None

    async def mark_seen(self, student_id: str, direction: str, ttl_seconds: int = 900):
        """O'quvchini ko'rilgan deb belgilash va TTL qo'yish"""
        key = f"debounce:{student_id}:{direction}"
        if self.redis_client:
            try:
                await self.redis_client.set(key, "1", ex=ttl_seconds)
                return
            except Exception:
                pass
        await self.fallback.set(key, "1", ex=ttl_seconds)


debounce_manager = DebounceManager()

