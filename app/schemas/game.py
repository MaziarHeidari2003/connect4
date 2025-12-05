from pydantic import BaseModel
import uuid as _uuid
import enum
from datetime import datetime


class GameStatus(str, enum.Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGESS"
    FINISHED = "FINISHED"
    TERMINATED = (
        "TERMINATED"  # For the games who have been pending or in-progress for a  while
    )


class GameSidesType(str, enum.Enum):
    OneSideBot = "OneSideBot"
    TwoSideBot = "TwoSideBot"
    TwoSideHuman = "TwoSideHuman"


class GameCreateSchema(BaseModel):
    uuid: _uuid.UUID | None = None
    board: list
    status: GameStatus | None = None
    created_by: int | None = None
    moves_count: int
    game_sides_type: GameSidesType


class GameUpdateSchema(BaseModel):
    board: list
    status: GameStatus | None = None
    player_1: int
    player_2: int
    winner: int


class GameResponse(BaseModel):
    uuid: _uuid.UUID
    status: GameStatus
    created: datetime
    player_1_nick_name: str | None = None
    player_2_nick_name: str | None = None
    creator_nick_name: str | None = None
    board: list
    current_turn_nick: str | None = None
    winner: str | None = None
    game_sides_type: GameSidesType

    class Config:
        from_attributes = True
