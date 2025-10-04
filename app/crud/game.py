from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.base import CRUDBase
from app.models import Game
from app.schemas import GameCreateSchema, GameUpdateSchema
from sqlalchemy.future import select


class CRUDGame(CRUDBase[Game, GameCreateSchema, GameUpdateSchema]):
    async def get_by_uuid(self, db: AsyncSession, _uuid: str):
        query = select(self.model).where(self.model.uuid == _uuid)
        return await self._first(db.scalars(query))


game = CRUDGame(Game)
