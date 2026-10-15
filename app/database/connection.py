from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.config import settings

async_engine = create_async_engine(
    settings.database.URL,
    echo=settings.database.ECHO,
    pool_size=settings.database.POOL_SIZE,
    max_overflow=settings.database.MAX_OVERFLOW,
    pool_pre_ping=settings.database.POOL_PRE_PING,
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine, expire_on_commit=False, autoflush=False
)
