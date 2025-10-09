from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.base import CRUDBase
from app.models import Game
from app.schemas import GameCreateSchema, GameUpdateSchema
from sqlalchemy.future import select
from app import schemas, models
from sqlalchemy.orm import aliased


class CRUDGame(CRUDBase[Game, GameCreateSchema, GameUpdateSchema]):
    async def get_game_and_players_by_uuid(self, db: AsyncSession, _uuid: str):
        p1 = aliased(models.Player)
        p2 = aliased(models.Player)
        turn = aliased(models.Player)
        winner = aliased(models.Player)
        # I can handle having the players' names in a smoother way, but I like these joins and there are some lessons for me here
        query = (
            select(
                self.model.status,
                self.model.created,
                self.model.board,
                self.model.uuid,
                p1.nick_name.label("player_1_nick"),
                p2.nick_name.label("player_2_nick"),
                turn.nick_name.label("current_turn_nick"),
                winner.nick_name.label("winner"),
            )
            .join(p1, self.model.player_1 == p1.id, isouter=True)
            .join(p2, self.model.player_2 == p2.id, isouter=True)
            .join(turn, self.model.current_turn == turn.id, isouter=True)
            .join(winner, self.model.winner == winner.id, isouter=True)
            .where(self.model.uuid == _uuid)
        )
        result = await db.execute(query)
        row = result.first()
        return row

    async def get_by_uuid(self, db: AsyncSession, _uuid: str):
        query = select(self.model).where(self.model.uuid == _uuid)
        return await self._first(db.scalars(query))

    async def get_pending_games(self, db: AsyncSession):
        query = (
            select(
                self.model.uuid,
                self.model.status,
                self.model.created,
                self.model.board,
                models.Player.nick_name.label("player_1_nick"),
            )
            .where(self.model.status == schemas.GameStatus.PENDING.value)
            .join(models.Player, self.model.player_1 == models.Player.id)
            .order_by(self.model.created)
        )
        result = await db.execute(query)
        return result.all()


game = CRUDGame(Game)
