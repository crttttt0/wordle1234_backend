from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from .connection import AsyncSessionLocal


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Выдает асинхронное подключение к БД и контроллирует commit и rollback."""

    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
