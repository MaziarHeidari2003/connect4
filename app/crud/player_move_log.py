from app.crud.base import CRUDBase
from app.models import PlayerMoveLog
from app.schemas import PlayerMoveLogCreateSchema, PlayerMoveLogUpdateSchema
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


class CRUDPlayerMoveLog(
    CRUDBase[PlayerMoveLog, PlayerMoveLogCreateSchema, PlayerMoveLogUpdateSchema]
):
    async def get_by_game_id_step(self, db: AsyncSession, game_id: int, step: int):
        query = select(self.model).where(
            self.model.related_game == game_id, self.model.step == step
        )
        return await self._first(db.scalars(query))


player_move_log = CRUDPlayerMoveLog(PlayerMoveLog)
