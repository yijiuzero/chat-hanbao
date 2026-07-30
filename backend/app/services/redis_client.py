"""
Redis 客户端 - 用于会话缓存
"""
import redis.asyncio as aioredis
from loguru import logger

from app.config import settings


class RedisClient:
    """异步 Redis 客户端封装"""

    def __init__(self):
        self._client: aioredis.Redis | None = None

    async def connect(self):
        """连接 Redis"""
        try:
            self._client = aioredis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
            )
            await self._client.ping()
            logger.info("✅ Redis 连接成功")
        except Exception as e:
            logger.warning(f"⚠️ Redis 连接失败，将使用内存缓存: {e}")
            self._client = None

    async def disconnect(self):
        """断开连接"""
        if self._client:
            await self._client.close()

    @property
    def client(self) -> aioredis.Redis | None:
        return self._client

    def is_connected(self) -> bool:
        return self._client is not None


# 全局 Redis 实例
redis_client = RedisClient()
