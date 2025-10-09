from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.base import CRUDBase
from app.models import Game
from app.schemas import GameCreateSchema, GameUpdateSchema
from sqlalchemy.future import select
from app import schemas, models


class CRUDGame(CRUDBase[Game, GameCreateSchema, GameUpdateSchema]):
    async def get_by_uuid(self, db: AsyncSession, _uuid: str):
        query = select(self.model).where(self.model.uuid == _uuid)
        return await self._first(db.scalars(query))

    async def get_pending_games(self, db: AsyncSession):
        query = (
            select(
                self.model.uuid,
                self.model.status,
                self.model.created,
                models.Player.nick_name,
            )
            .where(self.model.status == schemas.GameStatus.PENDING.value)
            .join(models.Player, self.model.player_1 == models.Player.id)
            .order_by(self.model.created)
        )
        result = await db.execute(query)
        return result.all()


game = CRUDGame(Game)
