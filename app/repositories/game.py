from sqlalchemy import select

from app.models import Game

from .base import BaseRepository


class GameRepository(BaseRepository[Game]):
    """Репозиторий для работы с партиями."""

    model = Game

    async def get_for_update(self, game_id: int) -> Game | None:
        """Заблокировать партию на время транзакции."""

        return await self.session.scalar(
            select(Game).where(Game.id == game_id).with_for_update()
        )
