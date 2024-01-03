import asyncio
from fastapi import FastAPI, WebSocket, Request, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from Client import Client
from ConnectionManager import ConnectionManager
from DownloadsManager import DownloadsManager
from my_logs_config import set_log_config

app = FastAPI(title="main")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
conn_manager = ConnectionManager()
down_manager = DownloadsManager()
asyncio.ensure_future(down_manager.advance_queue())
set_log_config()

@app.get("/")
async def get(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
    # with open("templates/index.html", "r", encoding="utf-8") as file:
    #     html_content = file.read()
    # return HTMLResponse(content=html_content)


@app.websocket("/download")
async def websocket_endpoint(websocket: WebSocket):
    await conn_manager.connect(websocket)
    client = Client(websocket=websocket, conn_manager=conn_manager, down_manager=down_manager)
    try:
        while True:
            await client.start()
    except WebSocketDisconnect:
        conn_manager.disconnect(websocket)
