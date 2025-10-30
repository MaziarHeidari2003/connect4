import asyncio
import websockets


async def test_ws():
    uri = "ws://127.0.0.1:8001/api/v1/game/426a4c87-5062-4e10-95a5-e7d14ced5819"
    async with websockets.connect(uri) as ws:
        print("Connected!")
        await ws.send("ping")
        response = await ws.recv()
        print("Received:", response)


asyncio.run(test_ws())
