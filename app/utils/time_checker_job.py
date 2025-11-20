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
from app.utils.publisher import publish_game_update


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


async def player_time_limit_check(game_uuid: uuid.UUID, current_turn: int):
    async with async_session() as db:
        game = await crud.game.get_by_uuid(db=db, _uuid=game_uuid)
        current_turn_player = await crud.player.get(db=db, id=game.current_turn)

        if game.current_turn == current_turn:
            winner_nick_name = (
                game.player_1_nick_name
                if current_turn == game.player_2
                else game.player_2_nick_name
            )
            loser_nick_name = (
                game.player_1_nick_name
                if current_turn == game.player_1
                else game.player_2_nick_name
            )
            game.winner_nick_name = winner_nick_name
            game.status = schemas.GameStatus.FINISHED
            game.winner = (
                game.player_1 if current_turn == game.player_2 else game.player_2
            )
            await crud.game.update(db=db, db_obj=game)
            await publish_game_update(
                game_uuid,
                {
                    "board": game.board,
                    "status": game.status,
                    "current_turn": current_turn_player.nick_name,
                    "current_turn_id": current_turn_player.id,
                    "winner": game.winner_nick_name,
                    "moves_count": game.moves_count,
                    "end_reason": f"{loser_nick_name} delayed too much and lost",
                },
            )
            print(
                f"Time is up for {current_turn_player.nick_name} and the winner is {winner_nick_name}"
            )


async def schedule_player_time(game_uuid: uuid.UUID, current_turn: int, move_num: int):
    scheduler_app.scheduler.add_job(
        player_time_limit_check,
        kwargs={
            "game_uuid": game_uuid,
            "current_turn": current_turn,
        },
        trigger="date",
        run_date=datetime.now() + timedelta(seconds=settings.TIME_LIMIT_TO_MAKE_MOVE),
        id=f"{move_num}_{str(game_uuid)}",
    )
