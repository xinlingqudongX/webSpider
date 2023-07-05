from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from .ws_manager import ConnectionManager


wsManager = ConnectionManager()
router = APIRouter()

@router.websocket('/ws')
async def websocket_endpoint(websocket: WebSocket):
    await wsManager.connect(websocket)
    # await websocket.accept()

    # data = await websocket.receive()
    # print(data)
    try:
        while True:
            data = await websocket.receive_text()
            print(data,'接收的数据')
            await wsManager.notify_all(data)   # 将传入的数据发送到所有活动连接
    except WebSocketDisconnect as err:
        print(err)
        await wsManager.disconnect(websocket)  # 客户端断开连接，调用连接管理器的disconnect()方法