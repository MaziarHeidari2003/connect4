from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.db.session import async_session
from apscheduler.jobstores.redis import RedisJobStore
from functools import wraps
import asyncio, uuid
from datetime import datetime, timedelta
from app import crud, schemas
from app.core.security import settings


class SchedulerApp:
    def __init__(self):
        jobstores = {
            "default": RedisJobStore(
                jobs_key="apscheduler.jobs",
                run_times_key="apscheduler.run_times",
                host=settings.REDIS_SERVER,
                port=settings.REDIS_PORT,
                db=0,
            )
        }

        self.scheduler = AsyncIOScheduler(jobstores=jobstores)


scheduler_app = SchedulerApp()


async def time_limit_checker(game_uuid: uuid.UUID):
    print(f"Background task for game {game_uuid} started")
    async with async_session() as db:
        game = await crud.game.get_by_uuid(db=db, _uuid=game_uuid)
        game.status = schemas.GameStatus.FINISHED
        if game.player_1 == game.current_turn:
            game.winner = game.player_2
        else:
            game.winner = game.player_1

        await crud.game.update(db=db, db_obj=game)


def schedule_checker(game_uuid: uuid.UUID, move_num: int):
    scheduler_app.scheduler.add_job(
        time_limit_checker,
        kwargs={"game_uuid": game_uuid},
        trigger="date",
        run_date=datetime.now() + timedelta(seconds=60),
        id=f"{move_num}_{str(game_uuid)}",
    )


def schedule_remover(game_uuid: uuid.UUID, move_num: int):
    scheduler_app.scheduler.remove_job(
        job_id=f"{move_num}_{str(game_uuid)}",
    )
