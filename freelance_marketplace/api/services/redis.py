import hashlib
import json
from enum import Enum
from typing import Any, Coroutine

import redis.asyncio as redis
from fastapi import HTTPException
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
    async def __get_redis_data(cache_key: str):
        try:
            redis_data = await redis_client.get(cache_key)
            if redis_data:
                return json.loads(redis_data)
            else:
                return None
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def get_redis_data(
            prefix: str = None,
            match: str = None,
            query_params: dict = None
    ) -> tuple[Any | None, str]:

        assert prefix or match
        assert not (prefix and match)
        if prefix:
            assert query_params
        if query_params:
            assert prefix

        if prefix:
            cache_key = await Redis.__generate_cache_key(query_params=query_params, prefix=prefix)
            return await Redis.__get_redis_data(cache_key=cache_key), cache_key
        if match:
            return await Redis.__get_redis_data(cache_key=match), match
        raise HTTPException(status_code=500, detail=f"Prefix or match not provided")




    @staticmethod
    async def set_redis_data(cache_key: str, data, ex: int = 3600):
        try:
            data_encoded = jsonable_encoder(data)
            await redis_client.set(cache_key, json.dumps(data_encoded), ex=ex)
            return True

        except Exception as e:
            print(f"{str(e)}")
            return False


    @staticmethod
    async def invalidate_cache(prefix: str):
        try:
            cursor, keys = await redis_client.scan(match=f"{prefix}*", count=100_000_000)
            if keys:
                await redis_client.delete(*keys)

            return True
        except Exception as e:
            print(f"Error invalidating cache for prefix {prefix}: {e}")
            return False

    @staticmethod
    async def __generate_cache_key(prefix: str, query_params: dict = None) -> str:
        filtered_params = {key: value for key, value in query_params.items() if value is not None}
        sorted_items = sorted(filtered_params.items())
        key_string = "&".join(f"{key}={value}" for key, value in sorted_items)
        #hash to avoid long keys.
        hashed_key = hashlib.md5(key_string.encode()).hexdigest()
        return f"{prefix}:{hashed_key}"


redis_client = Redis().get_client()

