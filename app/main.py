import datetime
import logging
from multiprocessing import Manager

from dotenv import dotenv_values
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from starlette.middleware.cors import CORSMiddleware

config = dotenv_values(".env")
engine = create_async_engine(
    f"mysql+aiomysql://{config['MYSQL_USER']}:{config['MYSQL_PASSWORD']}@{config['MYSQL_HOST']}/{config['MYSQL_DATABASE']}")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)
manager = Manager()
store = manager.dict()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root(request: Request):
    date = datetime.datetime.now().isoformat()
    user_agent = request.headers.get('User-Agent')
    async with SessionLocal() as session:
        await session.execute(
            f"INSERT INTO counters(datetime, client_info, value) VALUES ('{date}','{user_agent}',{store['count']})")
        await session.commit()
    return store['count']


@app.get("/stat")
async def counter(request: Request):
    store["count"] = store["count"] + 1
    date = datetime.datetime.now().isoformat()
    user_agent = request.headers.get('User-Agent')
    async with SessionLocal() as session:
        await session.execute(
            f"INSERT INTO counters(datetime, client_info, value) VALUES ('{date}','{user_agent}',{store['count']})")
        await session.commit()

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
    async with SessionLocal() as session:
        res = await session.execute(
            f"SELECT value FROM counters ORDER BY datetime DESC LIMIT 1")
        count = res.scalar()
        if not count:
            store["count"] = 0
        else:
            store["count"] = count
