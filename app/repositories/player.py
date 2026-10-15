from collections.abc import Sequence

from sqlalchemy import func, select, update

from app.core.enums import GameStatus
from app.models import Game, Player

from .base import BaseRepository


class PlayerRepository(BaseRepository[Player]):
    """Репозиторий для работы с игроками."""

    model = Player

    async def get_by_username(self, username: str) -> Player | None:
        """Получить игрока по никнейму."""

        return await self.session.scalar(
            select(Player).where(Player.username == username)
        )

    async def add_points(self, player_id: int, points: int) -> None:
        """Атомарно увеличить сумму очков игрока."""

        await self.session.execute(
            update(Player)
            .where(Player.id == player_id)
            .values(total_points=Player.total_points + points)
        )

    async def get_leaderboard(self, limit: int) -> Sequence[Player]:
        """Получить топ игроков по очкам."""

        result = await self.session.scalars(
            select(Player)
            .order_by(Player.total_points.desc(), Player.username.asc())
            .limit(limit)
        )
        return result.all()

    async def get_stats(self, player_id: int) -> dict[str, int]:
        """Собрать агрегированную статистику игрока."""

        games_played = (
            await self.session.scalar(
                select(func.count())
                .select_from(Game)
                .where(
                    Game.player_id == player_id,
                    Game.status != GameStatus.IN_PROGRESS,
                )
            )
            or 0
        )
        games_won = (
            await self.session.scalar(
                select(func.count())
                .select_from(Game)
                .where(Game.player_id == player_id, Game.status == GameStatus.WON)
            )
            or 0
        )
        best_score = (
            await self.session.scalar(
                select(func.coalesce(func.max(Game.score), 0)).where(
                    Game.player_id == player_id
                )
            )
            or 0
        )

        statuses = await self.session.scalars(
            select(Game.status)
            .where(Game.player_id == player_id, Game.status != GameStatus.IN_PROGRESS)
            .order_by(Game.finished_at.desc())
        )
        streak = 0
        for status in statuses:
            if status != GameStatus.WON:
                break
            streak += 1

        return {
            "games_played": games_played,
            "games_won": games_won,
            "best_score": best_score,
            "current_streak": streak,
        }
