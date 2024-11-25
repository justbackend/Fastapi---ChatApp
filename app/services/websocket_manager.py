from starlette.websockets import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active_connections = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        try:
            self.active_connections.remove(websocket)
        except:
            pass

    async def send_message(self, message: str, websocket):
        for connection in self.active_connections:
            if websocket != connection:
                await connection.send_text(message)

manager = ConnectionManager()
