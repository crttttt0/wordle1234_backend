from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import GameStatus
from app.database import Base

if TYPE_CHECKING:
    from .player import Player


class Game(Base):
    """Партия игрока."""

    __tablename__ = "games"

    id: Mapped[int] = mapped_column(primary_key=True)
    answer: Mapped[str] = mapped_column(String(5))
    status: Mapped[GameStatus] = mapped_column(
        Enum(
            GameStatus,
            native_enum=False,
            length=20,
            values_callable=lambda enum: [member.value for member in enum],
        ),
        default=GameStatus.IN_PROGRESS,
    )
    attempts_used: Mapped[int] = mapped_column(default=0)
    score: Mapped[int | None] = mapped_column(default=None)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), default=None
    )

    player_id: Mapped[int] = mapped_column(
        ForeignKey("players.id", ondelete="CASCADE"), index=True
    )

    player: Mapped[Player] = relationship(back_populates="games", lazy="raise")
