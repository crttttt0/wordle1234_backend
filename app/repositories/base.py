from typing import Generic, Sequence, TypeVar

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Базовый репозиторий с общими CRUD-операциями."""

    model: type[ModelType]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_all(self, page: int = 1, limit: int = 20) -> Sequence[ModelType]:
        """Получить страницу записей."""

        result = await self.session.scalars(
            select(self.model).offset(limit * (page - 1)).limit(limit)
        )
        return result.all()

    async def count(self) -> int:
        """Получить общее количество записей."""

        return (
            await self.session.scalar(select(func.count()).select_from(self.model)) or 0
        )

    async def get_by_id(self, obj_id: int) -> ModelType | None:
        """Получить запись по id."""

        return await self.session.scalar(
            select(self.model).where(self.model.id == obj_id)
        )

    async def create(self, **kwargs) -> ModelType:
        """Создать новую запись."""

        obj = self.model(**kwargs)

        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)

        return obj

    async def update(self, obj: ModelType, **kwargs) -> ModelType:
        """Обновить существующую запись."""

        for key, value in kwargs.items():
            setattr(obj, key, value)

        await self.session.flush()
        await self.session.refresh(obj)

        return obj

    async def delete(self, obj: ModelType) -> None:
        """Удалить запись."""

        await self.session.delete(obj)
        await self.session.flush()
