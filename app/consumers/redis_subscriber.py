import json
from app.utils.redis_connector import redis_connector
from app.utils.connection_manager import (
    connection_manager,
)


async def subscribe_to_game_updates():
    redis_client = await redis_connector.get_redis_client()
    if not redis_client:
        print("Could not connect to Redis. Exiting subscriber.")
        return

    pubsub = redis_client.pubsub()
    await pubsub.subscribe("game_updates")

    print("Subscribed to Redis channel: game_updates")

    async for message in pubsub.listen():
        if message is None or message["type"] != "message":
            continue

        try:
            payload = json.loads(message["data"])
            game_uuid = payload["game_uuid"]
            data = payload["data"]

            await connection_manager.broadcast_update(game_uuid, data)
        except Exception as e:
            print(f"Redis subscriber error: {e}")
