from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps
from app import schemas, models, crud
import uuid
from app.utils.helpers import winner_move

router = APIRouter()


@router.post("/")
async def create_game(
    current_player: models.Player = Depends(deps.get_current_user),
    db: AsyncSession = Depends(deps.get_db_async),
):
    game_create_data = schemas.GameCreateSchema(
        board=[
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
        ],
        uuid=uuid.uuid4(),
        player_1=current_player.id,
        status=schemas.GameStatus.PENDING.value,
        current_turn=current_player.id,
    )

    return await crud.game.create(db=db, obj_in=game_create_data)


@router.patch("/join")
async def join_game(
    game_uuid: str,
    current_player: models.Player = Depends(deps.get_current_user),
    db: AsyncSession = Depends(deps.get_db_async),
):
    game = await crud.game.get_by_uuid(db=db, _uuid=game_uuid)
    game.player_2 = current_player.id
    game.status = schemas.GameStatus.IN_PROGRESS.value
    game = await crud.game.update(db=db, db_obj=game)
    return game


@router.patch("/make-move")
async def make_move(
    game_uuid: str = Query(...),
    chosen_column: int = Body(...),
    db: AsyncSession = Depends(deps.get_db_async),
    current_player: models.Player = Depends(deps.get_current_user),
):
    game = await crud.game.get_by_uuid(db=db, _uuid=game_uuid)
    if current_player.id != game.current_turn:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="It is not your turn"
        )

    player_move = 1 if current_player.id == game.player_1 else 2
    board = game.board
    if board[chosen_column].count(1) + board[chosen_column].count(2) == 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="This column is full"
        )
    print(board)
    last_0_index = len(board[chosen_column]) - 1 - board[chosen_column][::-1].index(0)
    board[chosen_column][last_0_index] = player_move
    print(board)
    game.board = board
    game.current_turn = (
        game.player_1 if current_player.id == game.player_2 else game.player_2
    )
    if winner_move(column_count=6, row_count=5, player_move=player_move, board=board):
        game.winner = current_player.id
        game.status = schemas.GameStatus.FINISHED
        return await crud.game.update(db=db, db_obj=game)
    return await crud.game.update(db=db, db_obj=game)
