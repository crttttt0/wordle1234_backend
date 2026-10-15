from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field

from app.core.enums import GameStatus


class GameStartResponse(BaseModel):
    """Ответ на создание партии."""

    id: Annotated[
        int,
        Field(
            description="Уникальный идентификатор партии.",
            examples=[7],
        ),
    ]
    answer: Annotated[
        str,
        Field(
            description="Загаданное слово партии.",
            examples=["cane"],
        ),
    ]
    word_length: Annotated[
        int,
        Field(
            description="Длина загаданного слова.",
            ge=1,
            examples=[4],
        ),
    ]
    max_attempts: Annotated[
        int,
        Field(
            description="Максимально допустимое число попыток.",
            ge=1,
            examples=[6],
        ),
    ]
    started_at: Annotated[
        datetime,
        Field(
            description="Момент начала партии.",
            examples=["2026-09-21T10:30:00Z"],
        ),
    ]


class GameFinishRequest(BaseModel):
    """Итог партии, присланный клиентом."""

    won: Annotated[
        bool,
        Field(
            description="Выиграна ли партия.",
            examples=[True],
        ),
    ]
    attempts_used: Annotated[
        int,
        Field(
            description="Количество использованных попыток, минимум одна.",
            ge=1,
            examples=[3],
        ),
    ]


class GameStateResponse(BaseModel):
    """Состояние партии."""

    id: Annotated[
        int,
        Field(
            description="Уникальный идентификатор партии.",
            examples=[7],
        ),
    ]
    status: Annotated[
        GameStatus,
        Field(
            description="Текущий статус партии.",
            examples=[GameStatus.IN_PROGRESS],
        ),
    ]
    answer: Annotated[
        str,
        Field(
            description="Загаданное слово партии.",
            examples=["cane"],
        ),
    ]
    attempts_used: Annotated[
        int,
        Field(
            description="Количество использованных попыток.",
            ge=0,
            examples=[3],
        ),
    ]
    max_attempts: Annotated[
        int,
        Field(
            description="Максимально допустимое число попыток.",
            ge=1,
            examples=[6],
        ),
    ]
    score: Annotated[
        int | None,
        Field(
            description="Очки за партию, пока не завершена — `null`.",
            examples=[850, None],
        ),
    ]
    started_at: Annotated[
        datetime,
        Field(
            description="Момент начала партии.",
            examples=["2026-09-21T10:30:00Z"],
        ),
    ]
    finished_at: Annotated[
        datetime | None,
        Field(
            description="Момент завершения партии, пока не завершена — `null`.",
            examples=["2026-09-21T10:35:00Z", None],
        ),
    ]
