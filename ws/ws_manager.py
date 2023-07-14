from typing import Set, List, Union, Tuple
from fastapi import FastAPI, WebSocket
import asyncio

class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        '''等待ws连接'''
        await websocket.accept()
        await self.notify_all("A new client has connected", websocket)
        self.active_connections.add(websocket)

    async def disconnect(self, websocket: WebSocket):
        '''断开ws连接'''
        self.active_connections.remove(websocket)
        await self.notify_all("A client has disconnected", websocket)

    async def notify_all(self, message: str, exclude: WebSocket):
        if self.active_connections:
            tasks = [ws.send_text(message) for ws in self.active_connections if ws != exclude]
            await asyncio.gather(*tasks)