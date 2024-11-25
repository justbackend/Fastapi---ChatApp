from fastapi import APIRouter
from fastapi.websockets import WebSocket
from starlette.websockets import WebSocketDisconnect

from app.services.websocket_manager import manager

router = APIRouter(
    prefix='/ws'
)

online_users = set()

@router.websocket('/chat')
async def send_message(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_message(data, websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

