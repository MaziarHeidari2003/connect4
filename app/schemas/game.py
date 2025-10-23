from pydantic import BaseModel
import uuid as _uuid
import enum
from datetime import datetime


class GameStatus(str, enum.Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGESS"
    FINISHED = "FINISHED"


class GameCreateSchema(BaseModel):
    uuid: _uuid.UUID | None = None
    board: list
    status: GameStatus | None = None
    player_1: int | None = None
    current_turn: int
    moves_count: int


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
    player_1_nick: str | None = None
    player_2_nick: str | None = None
    board: list
    current_turn_nick: str | None = None
    winner: str | None = None

    class Config:
        from_attributes = True


class PendingGameResponse(BaseModel):
    uuid: _uuid.UUID
    status: GameStatus
    created: datetime
    player_1_nick: str | None = None
    player_2_nick: str | None = None
    board: list

    class Config:
        from_attributes = True
