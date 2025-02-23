from typing import Any, Optional
import redis
import json
from datetime import timedelta

class IslamicDataCache:
    def __init__(self, redis_url: str):
        self.redis_client = redis.from_url(redis_url)
        
    async def get_cached_data(self, key: str) -> Optional[Any]:
        data = await self.redis_client.get(key)
        return json.loads(data) if data else None
        
    async def cache_data(self, 
                        key: str, 
                        data: Any,
                        expiry: timedelta = timedelta(hours=24)) -> None:
        await self.redis_client.setex(
            key,
            expiry,
            json.dumps(data)
        ) 