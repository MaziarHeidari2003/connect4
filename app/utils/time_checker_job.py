from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.db.session import async_session
from apscheduler.jobstores.redis import RedisJobStore
from functools import wraps
import asyncio, uuid
from datetime import datetime, timedelta
from app import crud, schemas
from app.core.security import settings
from app.utils.connection_manager import connection_manager


class SchedulerApp:
    def __init__(self):
        jobstores = {
            "default": RedisJobStore(
                jobs_key="apscheduler.jobs",
                run_times_key="apscheduler.run_times",
                host=settings.REDIS_SERVER,
                port=settings.REDIS_PORT,
                username=settings.REDIS_USERNAME,
                password=settings.REDIS_PASSWORD,
                db=0,
            )
        }

        self.scheduler = AsyncIOScheduler(jobstores=jobstores)


scheduler_app = SchedulerApp()


async def time_limit_checker(game_uuid: uuid.UUID):
    print(f"Background task for game {game_uuid} started")
    async with async_session() as db:
        game = await crud.game.get_by_uuid(db=db, _uuid=game_uuid)
        if game.status == schemas.GameStatus.PENDING:
            game.status = schemas.GameStatus.FINISHED
        await crud.game.update(db=db, db_obj=game)


def schedule_checker(game_uuid: uuid.UUID):
    scheduler_app.scheduler.add_job(
        time_limit_checker,
        kwargs={"game_uuid": game_uuid},
        trigger="date",
        run_date=datetime.now() + timedelta(seconds=180),
        id=f"{game_uuid}",
    )


def schedule_remover(game_uuid: uuid.UUID, move_num: int):
    scheduler_app.scheduler.remove_job(
        job_id=f"{move_num}_{str(game_uuid)}",
    )


async def player_time_limit_check(
    game_uuid: uuid.UUID, current_turn: str, move_num: int
):
    async with async_session() as db:
        game = await crud.game.get_by_uuid(db=db, _uuid=game_uuid)
        if game.current_turn == current_turn:
            game.status = schemas.GameStatus.FINISHED
            game.winner = game.player_1 if current_turn == "player2" else game.player_2
            game.moves_count = move_num
            await crud.game.update(db=db, db_obj=game)
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
            print('Broadcast to all connected sockets done')


async def schedule_player_time(game_uuid: uuid.UUID, current_turn: str, move_num: int):
    scheduler_app.scheduler.add_job(
        player_time_limit_check,
        kwargs={
            "game_uuid": game_uuid,
            "current_turn": current_turn,
            "move_num": move_num,
        },
        trigger="date",
        run_date=datetime.now() + timedelta(seconds=settings.TIME_LIMIT_TO_MAKE_MOVE),
        id=f"{move_num}_{str(game_uuid)}",
    )
