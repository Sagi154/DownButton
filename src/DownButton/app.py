import logging

from fastapi import FastAPI, WebSocket, Request, WebSocketDisconnect
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from Client import Client
from pathlib import Path

from ConnectionManager import ConnectionManager

app = FastAPI(title= "main")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
manager = ConnectionManager()


@app.get("/")
async def get(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
    # with open("templates/index.html", "r", encoding="utf-8") as file:
    #     html_content = file.read()
    # return HTMLResponse(content=html_content)


@app.websocket("/download")
async def websocket_endpoint(websocket: WebSocket):
    # await websocket.accept()
    logging.basicConfig(format="[%(levelname)s] %(asctime)s %(message)s",
                        datefmt="%Y-%m-%d %H:%M:%S",
                        encoding='utf-8',
                        handlers=[logging.FileHandler("my_logs.log"),
                                  logging.StreamHandler()],
                        level=logging.INFO)
    await manager.connect(websocket)
    client = Client(websocket, manager)
    try:
        while True:
            await client.start()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
