from enum import Enum
from typing import List

from fastapi import APIRouter, FastAPI, Request
from starlette.websockets import WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


templates = Jinja2Templates(directory="templates")


router = APIRouter()


class ClientTypes(Enum):
    ADMIN = "admin"
    NODEMCU = "node"
    CLIENT = "viewer"


async def read_json(websocket: WebSocket):
    try:
        while True:
            yield await websocket.receive_json()
    except WebSocketDisconnect:
        pass


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.device_connection = None

    async def connect(self, websocket: WebSocket, client: ClientTypes, key=None):
        await websocket.accept()


        if client == ClientTypes.NODEMCU:
            self.device_connection = websocket
            await self.broadcast({"type": "device", "status": "connected"})
        else:
            self.active_connections.append(websocket)

        await websocket.send_json({"type": "connection", "status": "connected"})

        async for data in read_json(websocket):
            if client == ClientTypes.NODEMCU:
                await self.from_boat(data)
            else:
                await self.from_client(data, websocket, client)

        await self.disconnect(websocket, client)

    async def disconnect(self, websocket: WebSocket, client: ClientTypes):
        if client == ClientTypes.BOAT:
            self.device_connection = None
            await self.broadcast({"type": "device", "status": "disconnected"})
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, param):
        for connection in self.active_connections:
            await connection.send_json(param)

    async def from_boat(self, data):
            await self.broadcast(data)

    async def from_client(self, data, websocket, client):
        if self.device_connection is not None:
            await self.device_connection.send_json(data)


manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, client: ClientTypes, key=None):
    await manager.connect(websocket, client, key)

app = FastAPI()
app.include_router(router)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
