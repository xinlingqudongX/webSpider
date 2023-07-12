from typing import Set, List, Union, Tuple
from fastapi import FastAPI, WebSocket
import asyncio

class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        '''等待ws连接'''
        await websocket.accept()
        await self.notify_all("A new client has connected")
        self.active_connections.add(websocket)

    async def disconnect(self, websocket: WebSocket):
        '''断开ws连接'''
        self.active_connections.remove(websocket)
        await self.notify_all("A client has disconnected")

    async def notify_all(self, message: str):
        if self.active_connections:
            tasks = [websocket.send_text(message) for websocket in self.active_connections]
            await asyncio.gather(*tasks)