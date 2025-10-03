from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.base import CRUDBase
from app.models import Player
from app.schemas import PlayerCreateSchema, PlayerUpdateSchema
from sqlalchemy.future import select
from sqlalchemy.orm import Session
from app.db.session import async_session
from app.utils.crud_cache import CrudCache

crud_cache_namespace = CrudCache.create_namespace("user")


class CRUDPlayer(CRUDBase[Player, PlayerCreateSchema, PlayerUpdateSchema]):
    async def get_by_email(self, db: AsyncSession, email: str):
        query = select(self.model).where(self.model.email == email)
        return await self._first(db.scalars(query))

    @CrudCache.on_kwargs(namespace=crud_cache_namespace, exclude_kwargs=["db"])
    async def get_with_cache(
        self, *, db: AsyncSession | None = None, id: int
    ) -> Player:
        query = select(Player).filter(Player.id == id)
        if not db:
            async with async_session() as db:
                return self._first(db.scalars(query))
        else:
            return self._first(db.scalars(query))


player = CRUDPlayer(Player)
