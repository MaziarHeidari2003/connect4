from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect_player(self, game_uuid: str, websocket: WebSocket):
        if (
            isinstance(game_uuid, str)
            and game_uuid.startswith('"')
            and game_uuid.endswith('"')
        ):
            game_uuid = game_uuid.strip('"')

        await websocket.accept()

        if game_uuid not in self.active_connections:
            self.active_connections[game_uuid] = []

        self.active_connections[game_uuid].append(websocket)

    async def disconnect_player(self, game_uuid: str, websocket: WebSocket):
        if game_uuid in self.active_connections:
            self.active_connections[game_uuid].remove(websocket)
            if not self.active_connections[game_uuid]:
                del self.active_connections[game_uuid]

    async def broadcast_update(self, game_uuid: str, data: dict):
        if game_uuid in self.active_connections:
            for ws in self.active_connections[game_uuid]:
                try:
                    await ws.send_json(data)
                except Exception:
                    print("no connections to game found")
                    await self.disconnect_player(game_uuid, ws)
        else:
            print("game not found")


connection_manager = ConnectionManager()
