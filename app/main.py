import logging

from fastapi import FastAPI
from multiprocessing import Manager

from fastapi.responses import HTMLResponse

manager = Manager()
store = manager.dict()
store["count"] = 0

app = FastAPI()


@app.get("/")
async def root():
    return store["count"]


@app.get("/stat")
async def counter():
    store["count"] = store["count"] + 1
    return store["count"]


@app.get("/about")
async def say_hello():
    name = "Mikhail Ivanov"
    html = f"<h3>Hello, {name}!</h3>"
    return HTMLResponse(content=html, status_code=200)


@app.on_event("startup")
async def startup_event():
    uv_logger = logging.getLogger("uvicorn.access")
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter(
            "%(process)d - %(processName)s - %(asctime)s - %(levelname)s - %(message)s"
        )
    )
    uv_logger.addHandler(handler)