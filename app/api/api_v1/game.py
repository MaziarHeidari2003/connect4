from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    WebSocketDisconnect,
    status,
    Query,
    WebSocket,
)
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps
from app import schemas, models, crud
import uuid, random
from app.utils.helpers import winner_move
from sqlalchemy.orm.attributes import flag_modified
from app.utils.time_checker_job import (
    schedule_checker,
    schedule_player_time,
    schedule_remover,
)
from app.utils.connection_manager import connection_manager
from app.core.security import settings
from app.utils.redis_lock import RedisMutex

router = APIRouter()


@router.post("/")
async def create_game(
    current_player: models.Player = Depends(deps.get_current_user),
    db: AsyncSession = Depends(deps.get_db_async),
) -> uuid.UUID:
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
        created_by=current_player.id,
        status=schemas.GameStatus.PENDING.value,
        moves_count=0,
    )

    game = await crud.game.create(db=db, obj_in=game_create_data)
    if settings.USE_APSCHEDULER:
        print(settings.USE_APSCHEDULER)
        schedule_checker(game_uuid=game.uuid)

    return game.uuid


@router.patch("/join")
async def join_game(
    game_uuid: str,
    current_player: models.Player = Depends(deps.get_current_user),
    db: AsyncSession = Depends(deps.get_db_async),
):
    if (
        isinstance(game_uuid, str)
        and game_uuid.startswith('"')
        and game_uuid.endswith('"')
    ):
        game_uuid = game_uuid.strip('"')

    game = await crud.game.get_by_uuid(db=db, _uuid=game_uuid)
    if not game:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="The game doesn't exist"
        )

    if game.status in (schemas.GameStatus.FINISHED, schemas.GameStatus.IN_PROGRESS):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You can't join this game, two players have taken the game",
        )

    creator = await crud.player.get(db=db, id=game.created_by)

    if random.choice([True, False]):
        game.player_1 = current_player.id
        game.player_1_nick_name = current_player.nick_name
        game.player_2 = game.created_by
        game.player_2_nick_name = creator.nick_name
    else:
        game.player_2 = current_player.id
        game.player_2_nick_name = current_player.nick_name
        game.player_1 = game.created_by
        game.player_1_nick_name = creator.nick_name
    game.current_turn = game.player_1
    game.status = schemas.GameStatus.IN_PROGRESS.value
    game = await crud.game.update(db=db, db_obj=game)

    await connection_manager.broadcast_update(
        game_uuid,
        {
            "board": game.board,
            "status": game.status,
            "current_turn": game.current_turn,
            "winner": game.winner,
            "moves_count": game.moves_count,
        },
    )
    await schedule_player_time(
        game_uuid=game.uuid, current_turn=game.current_turn, move_num=1
    )

    return True


@router.patch("/make-move")
async def make_move(
    game_uuid: str = Query(...),
    chosen_column: int = Query(
        ..., description="The column you want to drop the ball in, from 0 to 6"
    ),
    db: AsyncSession = Depends(deps.get_db_async),
    current_player: models.Player = Depends(deps.get_current_user),
) -> bool:
    async with RedisMutex(name=str(game_uuid)):

        if (
            isinstance(game_uuid, str)
            and game_uuid.startswith('"')
            and game_uuid.endswith('"')
        ):
            game_uuid = game_uuid.strip('"')

        game = await crud.game.get_by_uuid(db=db, _uuid=game_uuid)
        if not game:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="The game doesn't exist"
            )
        if current_player.id != game.current_turn:
            game.winner = (
                game.player_1 if game.player_1 != current_player.id else game.player_2
            )
            game.winner_nick_name = (
                game.player_1_nick_name
                if game.player_1 != current_player.id
                else game.player_2_nick_name
            )
            game.status = schemas.GameStatus.FINISHED
            await crud.game.update(db=db, db_obj=game)

            await connection_manager.broadcast_update(
                game_uuid,
                {
                    "board": game.board,
                    "status": game.status,
                    "winner": game.winner_nick_name,
                    "moves_count": game.moves_count,
                },
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="It was't your turn. You lost the game honey.",
            )

        if game.status == schemas.GameStatus.FINISHED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="The game is over"
            )
        if game.status == schemas.GameStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The game is not started yet",
            )

        if chosen_column > 6 or chosen_column < 0:
            game.winner = (
                game.player_1 if game.player_1 != current_player.id else game.player_2
            )
            game.winner_nick_name = (
                game.player_1_nick_name
                if game.player_1 != current_player.id
                else game.player_2_nick_name
            )
            game.status = schemas.GameStatus.FINISHED
            await crud.game.update(db=db, db_obj=game)

            await connection_manager.broadcast_update(
                game_uuid,
                {
                    "board": game.board,
                    "status": game.status,
                    "winner": game.winner_nick_name,
                    "moves_count": game.moves_count,
                },
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Chosen column index is not valid. You lost the game honey",
            )

        player_move = 1 if current_player.id == game.player_1 else 2
        board = game.board
        if board[chosen_column].count(1) + board[chosen_column].count(2) == 6:
            game.winner = (
                game.player_1 if game.player_1 != current_player.id else game.player_2
            )
            game.winner_nick_name = (
                game.player_1_nick_name
                if game.player_1 != current_player.id
                else game.player_2_nick_name
            )
            game.status = schemas.GameStatus.FINISHED
            await crud.game.update(db=db, db_obj=game)

            await connection_manager.broadcast_update(
                game_uuid,
                {
                    "board": game.board,
                    "status": game.status,
                    "winner": game.winner_nick_name,
                    "moves_count": game.moves_count,
                },
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This column is full, You lost the game honey,",
            )

        last_0_index = board[chosen_column].index(0)
        board[chosen_column][last_0_index] = player_move
        game.board = board
        game.current_turn = (
            game.player_1 if current_player.id == game.player_2 else game.player_2
        )
        flag_modified(game, "board")
        game.moves_count += 1

        if winner_move(
            column_count=6, row_count=5, player_move=player_move, board=board
        ):
            game.winner = current_player.id
            game.winner_nick_name = current_player.nick_name
            game.status = schemas.GameStatus.FINISHED

        if game.moves_count == 42 and (not game.winner):
            game.status = schemas.GameStatus.FINISHED

        game = await crud.game.update(db=db, db_obj=game)
        current_turn_player = await crud.player.get(db=db, id=game.current_turn)
        await connection_manager.broadcast_update(
            game_uuid,
            {
                "board": game.board,
                "status": game.status,
                "current_turn": current_turn_player.nick_name,
                "winner": game.winner_nick_name,
                "moves_count": game.moves_count,
            },
        )

        player_move_log = schemas.PlayerMoveLogCreateSchema(
            current_player_turn=current_player.nick_name,
            board_status=game.board,
            game_status=game.status,
            related_game=game.id,
            step=game.moves_count,
        )
        await crud.player_move_log.create(db=db, obj_in=player_move_log)

        try:
            schedule_remover(game_uuid=game.uuid, move_num=game.moves_count)
            print(f"{game.uuid} removed from the scheduler")
        except Exception as e:
            print(e)

        await schedule_player_time(
            current_turn=game.current_turn,
            game_uuid=game.uuid,
            move_num=game.moves_count + 1,
        )

        return True


@router.get("/")
async def get_games(
    db: AsyncSession = Depends(deps.get_db_async),
    current_player: models.Player = Depends(deps.get_current_user),
    game_status: schemas.GameStatus = schemas.GameStatus.PENDING.value,
) -> list[schemas.PendingGameResponse]:

    results = await crud.game.get_games(db=db, game_status=game_status)
    pydantic_game_schema = []

    for result in results:
        pydantic_game_schema.append(schemas.PendingGameResponse.from_orm(result))

    return pydantic_game_schema


@router.get("/current")
async def get_current_game(
    db: AsyncSession = Depends(deps.get_db_async),
    current_player: models.Player = Depends(deps.get_current_user),
    game_uuid: str = Query(...),
) -> schemas.GameResponse:

    if (
        isinstance(game_uuid, str)
        and game_uuid.startswith('"')
        and game_uuid.endswith('"')
    ):
        game_uuid = game_uuid.strip('"')

    game = await crud.game.get_game_and_players_by_uuid(db=db, _uuid=game_uuid)
    if not game:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="The game doesn't exist"
        )
    pydantic_game_schema = schemas.GameResponse.from_orm(game)

    return pydantic_game_schema


@router.get("/review_game")
async def review_finished_game_steps(
    db: AsyncSession = Depends(deps.get_db_async),
    current_player: models.Player = Depends(deps.get_current_user),
    game_uuid: str = Query(...),
    game_step: int = Query(None),
):
    if (
        isinstance(game_uuid, str)
        and game_uuid.startswith('"')
        and game_uuid.endswith('"')
    ):
        game_uuid = game_uuid.strip('"')

    game = await crud.game.get_by_uuid(db=db, _uuid=game_uuid)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    print(game_step)
    if not game_step:
        game_step = game.moves_count
    print(game.moves_count)
    specific_game_step = await crud.player_move_log.get_by_game_id_step(
        db=db, game_id=game.id, step=game_step
    )
    print(specific_game_step)
    print(game_step)
    if not specific_game_step:
        raise HTTPException(status_code=404, detail="No move log found for this step")

    return schemas.PlayerMoveLogResponseSchema.from_orm(specific_game_step)


@router.websocket("/{game_uuid}")
async def websocket_endpoint(websocket: WebSocket, game_uuid: str):
    if (
        isinstance(game_uuid, str)
        and game_uuid.startswith('"')
        and game_uuid.endswith('"')
    ):
        game_uuid = game_uuid.strip('"')

    await connection_manager.connect_player(game_uuid, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await connection_manager.disconnect_player(game_uuid, websocket)


@router.get("/current_player_active_game")
async def get_current_player_game_uuid(
    db: AsyncSession = Depends(deps.get_db_async),
    current_player: models.Player = Depends(deps.get_current_user),
):
    active_game_uuid = await crud.game.get_current_player_active_game_uuid(
        db=db, player_id=current_player.id
    )

    return active_game_uuid
