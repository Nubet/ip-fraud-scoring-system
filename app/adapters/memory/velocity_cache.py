import asyncio

from cachetools import TTLCache

from app.domain.interfaces import VelocityCache


class TTLVelocityCache(VelocityCache):
    def __init__(self, ttl_seconds: int = 60, max_size: int = 100_000):
        self._cache = TTLCache(maxsize=max_size, ttl=ttl_seconds)
        self._lock = asyncio.Lock()

    async def increment_and_get_requests(self, ip: str) -> int:
        async with self._lock:
            current = self._cache.get(ip, 0) + 1
            self._cache[ip] = current
            return current
