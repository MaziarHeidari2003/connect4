from typing import Any, List, Optional, Union

from pydantic import EmailStr, PostgresDsn, RedisDsn, field_validator, ValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict

REDIS_ACTIVE_FLOW_NAMESPACE: str = "recom-system:flow:flow_id_{}:services_{}:action_{}"
REDIS_ACTIVE_PHONE_NAMESPACE: str = (
    "recom-system:phone_{}:flow_id_{}:services_{}:action_{}"
)


class AsyncPostgresDsn(PostgresDsn):
    allowed_schemes = {"postgres+asyncpg", "postgresql+asyncpg"}


class Settings(BaseSettings):
    TZ: str = "Asia/Tehran"
    CORS_ALLOWED_ORIGINS: List[str]
    CRUD_CACHE_REDIS_EXPIRATION_TIME: int = 60 * 20  # 20 min
    CRUD_CACHE_BASE_NAMESPACE: str = "connect4_crud:"

    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: str

    REDIS_PASSWORD: str | None
    REDIS_SERVER: str | None
    REDIS_PORT: int = 5432
    REDIS_USERNAME: str | None

    PROJECT_NAME: str
    API_V1_STR: str = "/api/v1"
    FIRST_SUPERUSER: EmailStr
    FIRST_SUPERUSER_PASSWORD: str
    DEBUG: bool = False

    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 1 * 7  # 7 days

    POSTGRESQL_ASYNC_DB_POOL_SIZE: int = 40
    POSTGRESQL_DB_POOL_SIZE: int = 20

    # NOTE: # This environment variable controls the number of messages pre-fetched by the consumer during data processing.
    # Increasing the prefetch count can improve processing speed by fetching more messages in advance,
    # but it may also introduce a higher risk of duplicate data and potentially affect data arrangement.
    # Consider adjusting this value based on your specific use case and performance requirements.
    # Be cautious when setting it to very high values as it may lead to inefficient resource utilization.
    # @see https://aio-pika.readthedocs.io/en/latest/rabbitmq-tutorial/2-work-queues.html#fair-dispatch
    CONSUMER_PREFETCH_COUNT: int = 1

    SUB_PATH: str = ""

    BACKEND_CORS_ORIGINS: List[str] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    @field_validator("SQLALCHEMY_DATABASE_URI", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], values: ValidationInfo) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            username=values.data.get("POSTGRES_USER"),
            password=values.data.get("POSTGRES_PASSWORD"),
            host=values.data.get("POSTGRES_SERVER"),
            port=int(values.data.get("POSTGRES_PORT")),
            path=f"{values.data.get('POSTGRES_DB') or ''}",
        )

    SQLALCHEMY_DATABASE_ASYNC_URI: Optional[AsyncPostgresDsn] = None

    @field_validator("SQLALCHEMY_DATABASE_ASYNC_URI", mode="before")
    @classmethod
    def assemble_async_db_connection(
        cls, v: Optional[str], values: ValidationInfo
    ) -> Any:
        if isinstance(v, str):
            return v
        return AsyncPostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=values.data.get("POSTGRES_USER"),
            password=values.data.get("POSTGRES_PASSWORD"),
            host=values.data.get("POSTGRES_SERVER"),
            port=int(values.data.get("POSTGRES_PORT")),
            path=f"{values.data.get('POSTGRES_DB') or ''}",
        )

    REDIS_URI: Optional[RedisDsn] = None

    @field_validator("REDIS_URI", mode="before")
    @classmethod
    def assemble_redis_URI_connection(cls, v: str | None) -> Any:
        if isinstance(v, str):
            return RedisDsn(v)

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
