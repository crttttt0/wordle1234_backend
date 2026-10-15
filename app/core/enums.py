from enum import StrEnum


class GameStatus(StrEnum):
    """Статус партии."""

    IN_PROGRESS = "in_progress"
    WON = "won"
    LOST = "lost"
