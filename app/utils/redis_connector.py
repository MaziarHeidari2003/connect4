import logging
from enum import IntEnum
from app.core.config import settings
import redis.asyncio as redis

logger = logging.getLogger(__name__)


class _RedisStatus(IntEnum):
    """Connection status for the redis client."""

    NONE = 0
    CONNECTED = 1
    AUTH_ERROR = 2
    CONN_ERROR = 3
    UNKNOWN_ERROR = 4


class RedisConnector:
    def __init__(self, redis_host_uri: str) -> None:
        self._client: redis.Redis = None
        self._redis_host_uri = redis_host_uri

    async def connect(
        self,
    ) -> tuple[_RedisStatus, redis.client.Redis]:  # pragma: no cover
        try:
            self._client = await redis.from_url(self._redis_host_uri)

            if self._client and await self._client.ping():
                return (_RedisStatus.CONNECTED, self._client)

            return (_RedisStatus.CONN_ERROR, None)

        except redis.AuthenticationError:
            return (_RedisStatus.AUTH_ERROR, None)

        except redis.ConnectionError:
            return (_RedisStatus.CONN_ERROR, None)

        except Exception as e:
            logger.error(f"Redis: {type(e)}:{e}")
            return (_RedisStatus.UNKNOWN_ERROR, None)

    async def check_or_fix_redis_connection(self) -> bool:
        if not self._client or not await self._client.ping():
            status, self._client = await self.connect()

            if status != _RedisStatus.CONNECTED:
                logger.error(f"RedisConnector: redis error: {status.name}")

                return False

        return True

    async def get_redis_client(self) -> redis.Redis | None:
        if await self.check_or_fix_redis_connection():
            return self._client
        return None


redis_connector = RedisConnector(
    redis_host_uri=f"redis://{settings.REDIS_USERNAME}:{settings.REDIS_PASSWORD}@{settings.REDIS_SERVER}:{settings.REDIS_PORT}/0"
)
