from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from app.core.config import settings
from sqlalchemy.orm import sessionmaker


engine_async = create_async_engine(
    str(settings.SQLALCHEMY_DATABASE_ASYNC_URI),
    pool_pre_ping=True,
    pool_size=settings.POSTGRESQL_ASYNC_DB_POOL_SIZE,
    max_overflow=10,
)
async_session = sessionmaker(
    bind=engine_async,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)
