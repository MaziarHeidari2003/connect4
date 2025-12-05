from app.db.base_class import Base
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import INTEGER, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.models import Player
from sqlalchemy.ext.mutable import MutableList


class Game(Base):
    id: Mapped[int] = mapped_column(INTEGER, primary_key=True)
    uuid: Mapped[str] = mapped_column(UUID(as_uuid=True), unique=True)
    status: Mapped[str] = mapped_column(String, nullable=True)
    board: Mapped[list] = mapped_column(MutableList.as_mutable(JSONB), default=list)
    moves_count: Mapped[int] = mapped_column(INTEGER, nullable=True, default=0)
    winner_nick_name: Mapped[str] = mapped_column(String, nullable=True)
    player_2_nick_name: Mapped[str] = mapped_column(String, nullable=True)
    player_1_nick_name: Mapped[str] = mapped_column(String, nullable=True)
    created_by: Mapped[int] = mapped_column(
        ForeignKey(Player.id, ondelete="SET NULL"), index=True, nullable=True
    )
    player_1: Mapped[int] = mapped_column(
        ForeignKey(Player.id, ondelete="SET NULL"), index=True, nullable=True
    )
    player_2: Mapped[int] = mapped_column(
        ForeignKey(Player.id, ondelete="SET NULL"), index=True, nullable=True
    )
    current_turn: Mapped[int] = mapped_column(
        ForeignKey(Player.id, ondelete="SET NULL"), index=True, nullable=True
    )
    winner: Mapped[int] = mapped_column(
        ForeignKey(Player.id, ondelete="SET NULL"), index=True, nullable=True
    )
    game_sides_type: Mapped[str] = mapped_column(String, nullable=True)
