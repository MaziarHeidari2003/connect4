from app.db.base_class import Base
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import INTEGER, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.models import Player


class Game(Base):
    id: Mapped[int] = mapped_column(INTEGER, primary_key=True)
    uuid: Mapped[str] = mapped_column(UUID(as_uuid=True), unique=True)
    status: Mapped[str] = mapped_column(String)
    board: Mapped[list] = mapped_column(JSONB, default=list)
    player_1: Mapped[int] = mapped_column(
        ForeignKey(Player.id, ondelete="SET NULL"), index=True, nullable=True
    )
    player_2: Mapped[int] = mapped_column(
        ForeignKey(Player.id, ondelete="SET NULL"), index=True, nullable=True
    )
    winner: Mapped[int] = mapped_column(
        ForeignKey(Player.id, ondelete="SET NULL"), index=True, nullable=True
    )
