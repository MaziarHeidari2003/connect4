from sqlalchemy.ext.asyncio import AsyncSession
from typing import Generic, TypeVar, Type, Any, Union, Awaitable
from app.db.base_class import Base
from sqlalchemy.future import select
from pydantic import BaseModel
from typing import Dict
from datetime import datetime

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
            await db.flush()
        return db_obj

    async def get(self, db: AsyncSession, id: Any):
        query = select(self.model).filter(self.model.id == id)
        return await self._first(db.scalars(query))

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

    def update(
        self,
        db: AsyncSession,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any], None] = None,
        commit: bool = True,
    ) -> Union[ModelType, Awaitable[ModelType]]:
        if obj_in is not None:
            obj_data = db_obj.__dict__
            if isinstance(obj_in, dict):
                update_data = obj_in
            else:
                update_data = obj_in.dict(exclude_unset=True)
            for field in obj_data:
                if field in update_data:
                    setattr(db_obj, field, update_data[field])
        if hasattr(self.model, "modified"):
            setattr(db_obj, "modified", datetime.now())
        db.add(db_obj)
        return self._commit_refresh(db=db, db_obj=db_obj, commit=commit)
