from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict

from freelance_marketplace.api.services.redis import redis_client


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}

    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        await redis_client.set(f"socket:{user_id}", "1", ex=3600)

    def disconnect(self, user_id: int):
        redis_client.delete(f"socket:{user_id}")

    async def is_online(self, user_id: str) -> bool:
        return await redis_client.exists(f"socket:{user_id}") > 0

    async def send_object(self, object: dict, user_id: int):
        websocket = redis_client.get(f"socket:{user_id}")
        if websocket:
            await websocket.send_json(object)

manager = ConnectionManager()