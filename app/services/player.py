from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING

from app.core.exceptions import (
    AuthenticationFailedException,
    EntityAlreadyExistsException,
    EntityNotFoundException,
)
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)

if TYPE_CHECKING:
    from app.models import Player
    from app.repositories import PlayerRepository


class PlayerService:
    """Бизнес-логика игроков."""

    def __init__(self, player_repository: PlayerRepository) -> None:
        self.player_repository = player_repository

    # Вспомогательные методы

    async def _get_by_username_or_raise(self, username: str) -> Player:
        """Получить игрока по никнейму или упасть с ошибкой, если не существует."""

        player = await self.player_repository.get_by_username(username)

        if player is None:
            raise EntityNotFoundException("Игрок не найден.")

        return player

    async def _check_player_not_exist(self, username: str) -> None:
        """Проверить по никнейму и успасть с ошибкой, если игрок существует."""

        player = await self.player_repository.get_by_username(username)

        if player is not None:
            raise EntityAlreadyExistsException("Никнейм занят.")

    def _issue_access_token(self, player: Player) -> dict[str, str]:
        """Выпускает access-токен для пользователя."""

        return {"access_token": create_access_token(data={"sub": player.username})}

    def _issue_refresh_token(self, player: Player) -> dict[str, str]:
        """Выпускает refresh-токен для пользователя."""

        return {"refresh_token": create_refresh_token(data={"sub": player.username})}

    def _issue_tokens(self, player: Player) -> dict[str, str]:
        """Выпускает пару access и refresh токенов."""

        return {
            **self._issue_access_token(player=player),
            **self._issue_refresh_token(player=player),
        }

    async def _authenticate(self, username: str, password: str) -> Player:
        """Проверить никнейм и пароль игрока."""

        try:
            player = await self._get_by_username_or_raise(username=username)
        except EntityNotFoundException:
            raise AuthenticationFailedException("Неверный никнейм или пароль.")

        if not await verify_password(
            plain_password=password, hashed_password=player.hashed_password
        ):
            raise AuthenticationFailedException("Неверный никнейм или пароль.")

        return player

    # Публичные методы

    async def register(self, username: str, password: str) -> Player:
        """Зарегистрировать нового игрока."""

        await self._check_player_not_exist(username=username)

        return await self.player_repository.create(
            username=username, hashed_password=await hash_password(password)
        )

    async def get_by_username(self, username: str) -> Player:
        """Получить игрока по никнейму или упасть с ошибкой, если не существует."""

        return await self._get_by_username_or_raise(username=username)

    async def login(self, username: str, password: str) -> dict[str, str]:
        """Логин пользователя."""

        player = await self._authenticate(username=username, password=password)
        return self._issue_tokens(player=player)

    async def refresh_token(self, refresh_token: str) -> dict[str, str]:
        """Выпускает новую пару токенов на основе refresh-токена, проверяя пользователя в БД."""

        payload = decode_token(token=refresh_token)
        if payload.get("type") != "refresh":
            raise AuthenticationFailedException("Неверный тип токена.")

        try:
            user = await self._get_by_username_or_raise(username=payload.get("sub"))
        except EntityNotFoundException:
            raise AuthenticationFailedException("Игрок не найден.")

        return self._issue_tokens(player=user)

    async def get_stats(self, player: Player) -> dict[str, int]:
        """Получить статистику игрока."""

        return await self.player_repository.get_stats(player.id)

    async def add_points(self, player_id: int, points: int) -> None:
        """Начислить игроку очки, проверив его существование."""

        player = await self.player_repository.get_by_id(obj_id=player_id)

        if player is None:
            raise EntityNotFoundException("Игрок не найден.")

        await self.player_repository.add_points(player_id=player_id, points=points)

    async def get_leaderboard(self, limit: int) -> Sequence[Player]:
        """Получить топ игроков по очкам."""

        return await self.player_repository.get_leaderboard(limit=limit)
