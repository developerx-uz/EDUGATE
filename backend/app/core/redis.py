import time
import asyncio
from typing import Optional, Dict, Any
from app.core.config import settings

try:
    import redis.asyncio as aioredis
    HAS_REDIS = True
except ImportError:
    HAS_REDIS = False


class InMemoryDebounceCache:
    """Redis yo'q bo'lsa yoki lokal sinovda ishlaydigan xotira kesh mexanizmi"""
    def __init__(self, max_entries: int = 10000):
        self._cache: Dict[str, tuple[float, str]] = {}
        self._max_entries = max_entries

    def _prune_if_needed(self, now: float):
        if len(self._cache) >= self._max_entries:
            expired = [k for k, (exp, _) in self._cache.items() if now > exp]
            for k in expired:
                del self._cache[k]
            if len(self._cache) >= self._max_entries:
                # Evict oldest quarter
                oldest = sorted(self._cache.items(), key=lambda item: item[1][0])[: self._max_entries // 4]
                for k, _ in oldest:
                    self._cache.pop(k, None)

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
        now = time.time()
        self._prune_if_needed(now)
        self._cache[key] = (now + ex, value)
        return True

    async def clear(self):
        self._cache.clear()


class DebounceManager:
    def __init__(self):
        self.redis_client = None
        self.fallback = InMemoryDebounceCache()

    async def initialize(self):
        if HAS_REDIS:
            try:
                client = aioredis.Redis(
                    host=settings.REDIS_HOST,
                    port=settings.REDIS_PORT,
                    db=settings.REDIS_DB,
                    decode_responses=True,
                    socket_connect_timeout=0.5,
                    socket_timeout=0.5
                )
                await asyncio.wait_for(client.ping(), timeout=0.5)
                self.redis_client = client
            except Exception:
                self.redis_client = None

    def get_status(self) -> Dict[str, Any]:
        return {
            "backend": "redis" if self.redis_client is not None else "memory",
            "connected": self.redis_client is not None,
        }

    async def is_debounced(self, student_id: str, direction: str) -> bool:
        """
        Anti-passback & Debounce:
        O'quvchi oxirgi DEBOUNCE_MINUTES ichida ayni shu yo'nalishda
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
