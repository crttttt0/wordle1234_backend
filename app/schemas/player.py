from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, computed_field


class PlayerRegisterRequest(BaseModel):
    """Запрос регистрации по никнейму и паролю."""

    username: Annotated[
        str,
        Field(
            min_length=1,
            max_length=255,
            description="Уникальный никнейм игрока.",
            examples=["mario_rossi"],
        ),
    ]
    password: Annotated[
        str,
        Field(
            min_length=8,
            max_length=128,
            description="Пароль игрока, от 8 до 128 символов.",
            examples=["s3cr3t-pass"],
        ),
    ]


class PlayerLoginRequest(PlayerRegisterRequest):
    """Запрос входа по никнейму и паролю."""


class RefreshRequest(BaseModel):
    """Запрос обновления access-токена."""

    refresh_token: Annotated[
        str,
        Field(
            description="Refresh-токен, выданный при входе.",
            examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."],
        ),
    ]


class TokenResponse(BaseModel):
    """Пара токенов."""

    access_token: Annotated[
        str,
        Field(
            description="Access-токен для авторизации запросов.",
            examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."],
        ),
    ]
    refresh_token: Annotated[
        str,
        Field(
            description="Refresh-токен для получения новой пары токенов.",
            examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."],
        ),
    ]
    token_type: Annotated[
        str,
        Field(
            "bearer",
            description="Тип токена, всегда `bearer`.",
            examples=["bearer"],
        ),
    ] = "bearer"


class PlayerResponse(BaseModel):
    """Данные игрока."""

    model_config = ConfigDict(from_attributes=True)

    id: Annotated[
        int,
        Field(
            description="Уникальный идентификатор игрока.",
            examples=[42],
        ),
    ]
    username: Annotated[
        str,
        Field(
            description="Уникальный никнейм игрока.",
            examples=["mario_rossi"],
        ),
    ]
    total_points: Annotated[
        int,
        Field(
            description="Сумма очков, набранных игроком за все партии.",
            examples=[1337],
        ),
    ]


class LeaderboardEntryResponse(BaseModel):
    """Строка таблицы лидеров."""

    model_config = ConfigDict(from_attributes=True)

    rank: Annotated[
        int,
        Field(
            description="Место игрока в таблице лидеров.",
            ge=1,
            examples=[1],
        ),
    ]
    username: Annotated[
        str,
        Field(
            description="Никнейм игрока.",
            examples=["mario_rossi"],
        ),
    ]
    total_points: Annotated[
        int,
        Field(
            description="Сумма очков, набранных игроком.",
            examples=[1337],
        ),
    ]


class PlayerStatsResponse(BaseModel):
    """Статистика игрока."""

    games_played: Annotated[
        int,
        Field(
            description="Общее количество сыгранных партий.",
            examples=[25],
        ),
    ]
    games_won: Annotated[
        int,
        Field(
            description="Количество выигранных партий.",
            examples=[18],
        ),
    ]
    current_streak: Annotated[
        int,
        Field(
            description="Текущая серия побед подряд.",
            examples=[5],
        ),
    ]
    best_score: Annotated[
        int,
        Field(
            description="Лучший результат за одну партию.",
            examples=[900],
        ),
    ]

    @computed_field(description="Доля выигранных партий от общего числа.")
    def win_rate(self) -> float:
        return self.games_won / self.games_played if self.games_played else 0.0
