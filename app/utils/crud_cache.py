import pickle, logging
from app.utils.redis_connector import redis_connector
from app.core.config import settings
from typing import Awaitable


logger = logging.getLogger(__name__)

REDIS_KEY_BLUE_PRINT = "{namespace}{kwargs_parts}"


class CrudCache:
    @staticmethod
    def create_namespace(namespace: str) -> str:
        return f"{settings.CRUD_CACHE_BASE_NAMESPACE}{namespace}"

    @staticmethod
    def dumps(obj: object) -> bytes:
        return pickle.dumps(obj, protocol=pickle.HIGHEST_PROTOCOL)

    @staticmethod
    def loads(data: bytes) -> object:
        return pickle.loads(data)

    @staticmethod
    async def get_by_key(redis_key: str):
        redis = await redis_connector.get_redis_client()
        if not redis:
            logger.warning("CrudCache.get_by_key_async: redis not connected")
            return None

        data = await redis.get(redis_key)
        if not data:
            return None

        return CrudCache.loads(data)

    @staticmethod
    async def set(redis_key: str, obj: object, ex: int):
        redis = await redis_connector.get_redis_client()
        if not redis:
            logger.warning("CrudCache.set_async: redis not connected")
            return None

        return await redis.set(name=redis_key, value=CrudCache.dumps(obj=obj), ex=ex)

    @staticmethod
    def generate_key(namespace: str, exclude_kwargs: list[str], kwargs: dict) -> str:
        kwargs_parts = ""

        for key, value in kwargs.items():
            if key in exclude_kwargs:
                continue

            kwargs_parts += f":{key}_{value}"

        redis_key = REDIS_KEY_BLUE_PRINT.format(
            namespace=namespace, kwargs_parts=kwargs_parts
        )

        return redis_key

    @staticmethod
    async def _invalidate(namespace: str) -> int:
        redis = await redis_connector.get_redis_client()
        if not redis:
            logger.warning("CrudCache.invalidate_async: redis not connected")
            return None

        keys_to_delete = await redis.keys(pattern=f"{namespace}*")
        if keys_to_delete:
            await redis.delete(*keys_to_delete)
        return len(keys_to_delete)

    @staticmethod
    def on_kwargs(
        namespace: str,
        exclude_kwargs: list[str],
        ex: int = settings.CRUD_CACHE_REDIS_EXPIRATION_TIME,
    ):
        def outer_wrapper(func: callable | Awaitable[callable]):

            async def inner_wrapper(*args, **kwargs):
                redis_key = CrudCache.generate_key(
                    namespace=namespace,
                    exclude_kwargs=exclude_kwargs,
                    kwargs=kwargs,
                )
                if obj := await CrudCache.get_by_key(redis_key=redis_key):
                    logger.debug(f"async, obj found in cache: {redis_key}")
                    return obj

                obj = await func(*args, **kwargs)
                logger.debug(f"async, obj save in cache: {redis_key}")
                await CrudCache.set(redis_key=redis_key, obj=obj, ex=ex)
                return obj

            return inner_wrapper

        return outer_wrapper
