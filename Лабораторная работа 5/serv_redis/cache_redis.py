import redis
from redis.asyncio import Redis
import os
import json

class RedisCache:
    def __init__(self):
        self.redis = None

    async def get_redis(self) -> Redis:
        if self.redis is None:
            REDIS_URL = os.getenv("REDIS_URL", "redis://cache:6379/0")
            self.redis = Redis.from_url(REDIS_URL, decode_responses=True)
        return self.redis

    async def cache_task(self, task: dict, ttl: int = 86400000):
        redis = await self.get_redis()
        task_id = task.get("code")
        value = json.dumps(task)

        await redis.setex(
            f"{task_id}",
            ttl,
            value
        )

    async def get_cached_task(self, task_id: str) -> dict | None:
        redis = await self.get_redis()
        key = f"{task_id}"
        task = await redis.get(key)
        return json.loads(task) if task else None

    async def remove_task(self, task_id: str):
        redis = await self.get_redis()
        await redis.delete(f"{task_id}")

    async def close(self):
        if self.redis and not self.redis.closed:
            await self.redis.close()