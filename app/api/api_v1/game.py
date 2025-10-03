from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps
from app import schemas, models, crud
import uuid

router = APIRouter()


@router.post("/")
async def create_game(
    _input: schemas.GameCreateSchema,
    current_player: models.Player = Depends(deps.get_current_user),
    db: AsyncSession = Depends(deps.get_db_async),
):
    _input.uuid = uuid.uuid4()
    _input.player_1 = current_player.id
    await crud.game.create(db=db, obj_in=_input)
    return True


async def join_game(
    game_uuid: str,
    current_player: models.Player = Depends(deps.get_current_user),
    db: AsyncSession = Depends(deps.get_db_async),
):
    pass
