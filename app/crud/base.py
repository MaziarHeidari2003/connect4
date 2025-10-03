from sqlalchemy.ext.asyncio import AsyncSession
from typing import Generic, TypeVar, Type, Any, Union, Awaitable
from app.db.base_class import Base
from sqlalchemy.future import select
from pydantic import BaseModel

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def _commit_refresh(
        self, db: AsyncSession, db_obj: ModelType, commit: bool = True
    ) -> ModelType:
        if commit:
            await db.commit()
            await db.refresh(db_obj)
        else:
            await db.refresh()
        return db_obj

    async def get(self, db: AsyncSession, id: Any):
        query = select(self.model).filter(self.model.id == id)
        return self._first(db.scalars(query))

    async def _first(self, scalars) -> Union[ModelType, None]:
        results = await scalars
        return results.first()

    async def get_multi(
        self, db: AsyncSession, skip: int = 0, limit: int | None = None
    ) -> Union[list[ModelType], Awaitable[list[ModelType]]]:
        query = select(self.model).offset(skip)
        if limit is None:
            return self._all(db.scalars(query))
        return self._all(db.scalars(query.limit(limit)))

    async def _all(self, scalars) -> list[ModelType]:
        results = await scalars
        return results.all()

    async def create(
        self, db: AsyncSession, obj_in: CreateSchemaType, commit: bool = True
    ) -> Union[ModelType, Awaitable[ModelType]]:

        if isinstance(obj_in, BaseModel):
            obj_in = obj_in.model_dump()
        elif not isinstance(obj_in, dict):
            obj_in = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in)  # type: ignore
        db.add(db_obj)
        return await self._commit_refresh(db=db, db_obj=db_obj, commit=commit)
