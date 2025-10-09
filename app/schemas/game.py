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


class GameUpdateSchema(BaseModel):
    board: list
    status: GameStatus | None = None
    player_1: int
    player_2: int
    winner: int


class PendingGameResponse(BaseModel):
    uuid: _uuid.UUID
    status: str
    created: datetime
    nick_name: str

    class Config:
        from_attributes = True
