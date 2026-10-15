from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.config import settings
from app.core.dependencies import get_current_player, get_player_service
from app.models import Player
from app.schemas.player import (
    LeaderboardEntryResponse,
    PlayerLoginRequest,
    PlayerRegisterRequest,
    PlayerResponse,
    PlayerStatsResponse,
    RefreshRequest,
    TokenResponse,
)
from app.services import PlayerService

router = APIRouter(prefix="/players", tags=["players"])


@router.post(
    "/register", response_model=PlayerResponse, status_code=status.HTTP_201_CREATED
)
async def register(
    player: PlayerRegisterRequest,
    player_service: Annotated[PlayerService, Depends(get_player_service)],
) -> Player:
    """Зарегистрировать игрока."""

    return await player_service.register(**player.model_dump())


@router.post("/login", response_model=TokenResponse)
async def login(
    player: PlayerLoginRequest,
    player_service: Annotated[PlayerService, Depends(get_player_service)],
) -> dict[str, str]:
    """Войти по никнейму и паролю."""

    return await player_service.login(**player.model_dump())


@router.post("/login/form", response_model=TokenResponse)
async def login_swagger(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    player_service: Annotated[PlayerService, Depends(get_player_service)],
) -> dict[str, str]:
    """Войти по никнейму и паролю."""

    return await player_service.login(
        username=form_data.username, password=form_data.password
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    refresh_token: RefreshRequest,
    player_service: Annotated[PlayerService, Depends(get_player_service)],
) -> dict[str, str]:
    """Обновить пару токенов по refresh-токену."""

    return await player_service.refresh_token(refresh_token=refresh_token.refresh_token)


@router.get("/me", response_model=PlayerResponse)
async def me(player: Annotated[Player, Depends(get_current_player)]) -> Player:
    """Вернуть текущего игрока."""

    return player


@router.get("/me/stats", response_model=PlayerStatsResponse)
async def stats(
    player: Annotated[Player, Depends(get_current_player)],
    player_service: Annotated[PlayerService, Depends(get_player_service)],
) -> dict[str, int]:
    """Вернуть статистику текущего игрока."""

    stats = await player_service.get_stats(player=player)

    return stats


@router.get("/leaderboard", response_model=list[LeaderboardEntryResponse])
async def get_leaderboard(
    player_service: Annotated[PlayerService, Depends(get_player_service)],
    limit: Annotated[int, Query(description="Лимит таблицы лидеров.")] = (
        settings.game.LEADERBOARD_SIZE
    ),
) -> list[LeaderboardEntryResponse]:
    """Вернуть топ игроков по очкам."""

    players = await player_service.get_leaderboard(limit=limit)

    return [
        LeaderboardEntryResponse(
            rank=rank,
            username=player.username,
            total_points=player.total_points,
        )
        for rank, player in enumerate(players, start=1)
    ]
