from pydantic import BaseModel
from app.schemas.game import GameStatus


class PlayerMoveLogBaseSchema(BaseModel):
    board_status: list
    game_status: GameStatus | None = None
    current_player_turn: str | None = None
    step: int | None = None


class PlayerMoveLogCreateSchema(PlayerMoveLogBaseSchema):
    related_game: int


class PlayerMoveLogUpdateSchema(PlayerMoveLogBaseSchema):
    pass


class PlayerMoveLogResponseSchema(PlayerMoveLogBaseSchema):

    class Config:
        from_attributes = True
