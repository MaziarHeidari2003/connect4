import logging

from app.utils.redis_connector import redis_connector

logger = logging.getLogger(__name__)


class RedisMutex:
    _PREFIX = "connect4_mutex"

    def __init__(self, name: str, timeout: int = 200) -> None:
        self._name = name
        self.timeout = timeout
        self.lock = None

    def get_name(self) -> str:
        return f"{self._PREFIX}:{self._name}"

    async def __aenter__(self):
        self.client = await redis_connector.get_redis_client()
        self.lock = self.client.lock(name=self.get_name(), timeout=self.timeout)
        await self.lock.acquire(blocking=True)
        logger.info(f"RedisMutex.__aenter__: lock: {self.get_name()}")

    async def __aexit__(self, exc_type, exc, tb):
        try:
            await self.lock.release()
            logger.info(f"RedisMutex.__aexit__: unlock: {self.get_name()}")
        except Exception as e:
            logger.error(f"RedisMutex.__aexit__: {e=}")
