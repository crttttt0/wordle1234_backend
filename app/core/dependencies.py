from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    AuthenticationFailedException,
    EntityNotFoundException,
)
from app.core.security import decode_token
from app.database import get_session
from app.models import Player
from app.repositories import GameRepository, PlayerRepository
from app.services import GameService, PlayerService
from app.services.word_provider import WordProvider, create_word_provider

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/players/login/form", auto_error=False
)


# Репозитории


def get_player_repository(
    session: Annotated[AsyncSession, Depends(get_session, scope="function")],
) -> PlayerRepository:
    """Собрать репозиторий игроков."""

    return PlayerRepository(session)


def get_game_repository(
    session: Annotated[AsyncSession, Depends(get_session, scope="function")],
) -> GameRepository:
    """Собрать репозиторий партий."""

    return GameRepository(session)


# Сервисы


def get_player_service(
    players: Annotated[PlayerRepository, Depends(get_player_repository)],
) -> PlayerService:
    """Собрать сервис игроков."""

    return PlayerService(players)


def get_word_provider() -> WordProvider:
    """Собрать провайдер загаданных слов."""

    return create_word_provider()


def get_game_service(
    games: Annotated[GameRepository, Depends(get_game_repository)],
    player_service: Annotated[PlayerService, Depends(get_player_service)],
    word_provider: Annotated[WordProvider, Depends(get_word_provider)],
) -> GameService:
    """Собрать сервис партий."""

    return GameService(games, player_service, word_provider)


# Аутентификация


async def get_current_player(
    token: Annotated[str | None, Depends(oauth2_scheme)],
    player_service: Annotated[PlayerService, Depends(get_player_service)],
) -> Player:
    """Вернуть текущего игрока по access-токену."""

    if token is None:
        raise AuthenticationFailedException("Токен не предоставлен.")

    payload = decode_token(token)

    if payload.get("type") != "access":
        raise AuthenticationFailedException("Неверный тип токена.")

    try:
        return await player_service.get_by_username(payload.get("sub"))
    except EntityNotFoundException:
        raise AuthenticationFailedException("Игрок не найден.")
