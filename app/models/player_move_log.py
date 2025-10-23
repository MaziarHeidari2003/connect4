from app.db.base_class import Base
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.models import Game


class PlayerMoveLog(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=False)
    board_status: Mapped[list] = mapped_column(
        MutableList.as_mutable(JSONB), default=list
    )
    current_player_turn: Mapped[str] = mapped_column(String)
    game_status: Mapped[str] = mapped_column(String)
    related_game: Mapped[int] = mapped_column(
        ForeignKey(Game.id, ondelete="SET NULL"), index=True, nullable=True
    )
    step: Mapped[int] = mapped_column(Integer, nullable=True, default=0)
