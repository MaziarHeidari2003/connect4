from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.base import CRUDBase
from app.models import Game
from app.schemas import GameCreateSchema, GameUpdateSchema
from sqlalchemy.future import select


class CRUDPlayer(CRUDBase[Game, GameCreateSchema, GameUpdateSchema]):
    pass


game = CRUDPlayer(Game)
