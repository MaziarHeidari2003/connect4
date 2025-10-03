from pydantic import BaseModel
import uuid
import enum


class GameStatus(str, enum.Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGESS"
    FINISHED = "FINISHED"


class GameCreateSchema(BaseModel):
    uuid: str | None = None
    board: list
    status: GameStatus | None = None
    player_1: int | None = None


class GameUpdateSchema(BaseModel):
    board: list
    status: GameStatus | None = None
    player1: int
    winner: int
