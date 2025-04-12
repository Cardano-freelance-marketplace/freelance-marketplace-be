import asyncio
import json
from enum import Enum
import redis.asyncio as redis
from fastapi.encoders import jsonable_encoder

from freelance_marketplace.core.config import settings
from freelance_marketplace.models.sql.sql_tables import Category, SubCategory


class RedisKeys(Enum):
    Category = ("categories:all", Category)
    SubCategory = ("subcategories:all", SubCategory)

    def __init__(self, redis_key, model):
        self.redis_key = redis_key
        self.model = model

class Redis:
    def __init__(self):
        self.client = None
        self.__init_redis()

    def __init_redis(self):
        self.client = redis.Redis(
            host=settings.redis.host,
            port=settings.redis.port,
            decode_responses=settings.redis.decode_responses
        )

    def get_client(self):
        return self.client

    @staticmethod
    async def get_redis_data(cache_key: str):
        redis_data = await redis_client.get(cache_key)
        if redis_data:
            return json.loads(redis_data)
        else:
            return None

    @staticmethod
    async def set_redis_data(cache_key: str, data):
        try:
            categories_encoded = jsonable_encoder(data)
            await redis_client.set(cache_key, json.dumps(categories_encoded), ex=3600)
            return True

        except Exception as e:
            print(f"{str(e)}")
            return False

    @staticmethod
    async def invalidate_cache(prefix: str):
        try:
            cursor, keys = await redis_client.scan(match=f"{prefix}*", count=1000)
            if keys:
                await redis_client.delete(*keys)

            return True
        except Exception as e:
            print(f"Error invalidating cache for prefix {prefix}: {e}")
            return False

redis_client = Redis().get_client()

