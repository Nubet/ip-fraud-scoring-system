import asyncio

from app.adapters.memory.velocity_cache import TTLVelocityCache


async def test_velocity_cache_increments_counter() -> None:
    cache = TTLVelocityCache(ttl_seconds=60, max_size=10)

    assert await cache.increment_and_get_requests("1.1.1.1") == 1
    assert await cache.increment_and_get_requests("1.1.1.1") == 2


async def test_velocity_cache_expires_entries() -> None:
    cache = TTLVelocityCache(ttl_seconds=1, max_size=10)

    assert await cache.increment_and_get_requests("2.2.2.2") == 1
    await asyncio.sleep(1.1)
    assert await cache.increment_and_get_requests("2.2.2.2") == 1
