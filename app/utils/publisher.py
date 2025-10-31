import json
from app.utils.redis_connector import redis_connector


async def publish_game_update(game_uuid: str, data: dict):
    redis_client = await redis_connector.get_redis_client()
    if not redis_client:
        print("Could not connect to Redis")
        return

    message = {
        "game_uuid": str(game_uuid),
        "data": data,
    }
    await redis_client.publish("game_updates", json.dumps(message))
