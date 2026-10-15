from __future__ import annotations

from datetime import datetime, timezone

from app.core.config import settings
from app.core.enums import GameStatus
from app.core.exceptions import (
    AccessDeniedException,
    BusinessRuleViolationException,
    EntityNotFoundException,
)
from app.models import Game, Player
from app.repositories import GameRepository

from .player import PlayerService
from .word_provider import WordProvider, generate_valid_answer


class GameService:
    """Бизнес-логика игровых партий."""

    def __init__(
        self,
        game_repository: GameRepository,
        player_service: PlayerService,
        word_provider: WordProvider,
    ) -> None:
        self.game_repository = game_repository
        self.player_service = player_service
        self.word_provider = word_provider

    # Вспомогательные методы

    async def _get_by_id_or_raise(self, player: Player, game_id: int) -> Game:
        """Получить партию игрока или выбросить исключение."""

        game = await self.game_repository.get_by_id(game_id)

        if game is None:
            raise EntityNotFoundException("Партия не найдена.")

        if game.player_id != player.id:
            raise AccessDeniedException("Можно просмотреть только свою партию.")

        return game

    async def _get_for_update_or_raise(self, player: Player, game_id: int) -> Game:
        """Заблокировать партию игрока или выбросить исключение."""

        game = await self.game_repository.get_for_update(game_id)

        if game is None:
            raise EntityNotFoundException("Партия не найдена.")

        if game.player_id != player.id:
            raise AccessDeniedException("Можно просмотреть только свою партию.")

        return game

    def _calculate_score(self, *, won: bool, attempts_used: int) -> int:
        """Посчитать очки за партию по числу использованных попыток."""

        if not won:
            return 0

        attempts_left = max(0, settings.game.MAX_ATTEMPTS - attempts_used + 1)

        return attempts_left * settings.game.POINTS_PER_ATTEMPT

    # Публичные методы

    async def start_game(self, player: Player) -> Game:
        """Создать новую партию со случайным словом."""

        answer = await generate_valid_answer(self.word_provider)

        return await self.game_repository.create(player_id=player.id, answer=answer)

    async def get_game(self, player: Player, game_id: int) -> Game:
        """Получить партию игрока."""

        return await self._get_by_id_or_raise(player=player, game_id=game_id)

    async def finish_game(
        self,
        player: Player,
        game_id: int,
        *,
        won: bool,
        attempts_used: int,
    ) -> Game:
        """Завершить партию и начислить очки."""

        game = await self._get_for_update_or_raise(player=player, game_id=game_id)

        if game.status != GameStatus.IN_PROGRESS:
            raise BusinessRuleViolationException("Партия уже завершена.")

        score = self._calculate_score(won=won, attempts_used=attempts_used)

        if score:
            await self.player_service.add_points(player_id=player.id, points=score)

        return await self.game_repository.update(
            game,
            status=GameStatus.WON if won else GameStatus.LOST,
            attempts_used=attempts_used,
            score=score,
            finished_at=datetime.now(timezone.utc),
        )
