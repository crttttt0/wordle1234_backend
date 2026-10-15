from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.core.config import settings
from app.core.dependencies import get_current_player, get_game_service
from app.models import Game, Player
from app.schemas.game import (
    GameFinishRequest,
    GameStartResponse,
    GameStateResponse,
)
from app.services import GameService

router = APIRouter(prefix="/games", tags=["games"])


def _to_state(game: Game) -> GameStateResponse:
    """Собрать ответ с состоянием партии."""

    return GameStateResponse(
        id=game.id,
        status=game.status,
        answer=game.answer,
        attempts_used=game.attempts_used,
        max_attempts=settings.game.MAX_ATTEMPTS,
        score=game.score,
        started_at=game.started_at,
        finished_at=game.finished_at,
    )


@router.post("", response_model=GameStartResponse, status_code=status.HTTP_201_CREATED)
async def start_game(
    player: Annotated[Player, Depends(get_current_player)],
    game_service: Annotated[GameService, Depends(get_game_service)],
) -> GameStartResponse:
    """Начать новую партию."""

    game = await game_service.start_game(player)

    return GameStartResponse(
        id=game.id,
        answer=game.answer,
        word_length=settings.game.WORD_LENGTH,
        max_attempts=settings.game.MAX_ATTEMPTS,
        started_at=game.started_at,
    )


@router.post("/{game_id}/finish", response_model=GameStateResponse)
async def finish_game(
    game_id: int,
    data: GameFinishRequest,
    player: Annotated[Player, Depends(get_current_player)],
    game_service: Annotated[GameService, Depends(get_game_service)],
) -> GameStateResponse:
    """Завершить партию по результату клиента."""

    game = await game_service.finish_game(
        player,
        game_id,
        won=data.won,
        attempts_used=data.attempts_used,
    )

    return _to_state(game)


@router.get("/{game_id}", response_model=GameStateResponse)
async def get_game(
    game_id: int,
    player: Annotated[Player, Depends(get_current_player)],
    game_service: Annotated[GameService, Depends(get_game_service)],
) -> GameStateResponse:
    """Получить состояние партии."""

    game = await game_service.get_game(player, game_id)

    return _to_state(game)
