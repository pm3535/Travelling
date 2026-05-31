import json
from typing import Any, Optional, Annotated
from idna import encode
import redis.asyncio as aioredis
from back.core.config import settings

redis_client: Optional[aioredis.Redis] = None

async def get_redis_client() -> Annotated[aioredis.Redis, "Redis client instance"]:
    global redis_client
    if redis_client is None:
        redis_client = aioredis.from_url(settings.redis_url, decode_responses=True, encoding="utf-8")

    return redis_client

async def set_cache(key: str, value: Any, expire_seconds: int = 3600) -> None:
    client = await get_redis_client()
    await client.set(key, json.dumps(value), ex=expire_seconds)

async def get_cache(key: str) -> Optional[Any]:
    client = await get_redis_client()
    value = await client.get(key)
    if value is not None:
        return json.loads(value)
    return None

async def delete_cache(key: str) -> None:
    client = await get_redis_client()
    await client.delete(key)

async def cache_delete_pattern(pattern: str) -> None:
    client = await get_redis_client()
    keys = await client.keys(pattern)
    if keys:
        await client.delete(*keys)





