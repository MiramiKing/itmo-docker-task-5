"""
Основной файл программы
"""

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
    f"mysql+aiomysql://{config['MYSQL_USER']}:{config['MYSQL_PASSWORD']}@{config['MYSQL_HOST']}/"
    f"{config['MYSQL_DATABASE']}")
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
    """
    Метод обрабатывающий корневой метод
    :param request: значение реквеста
    :return: значение счетчика
    """
    date = datetime.datetime.now().isoformat()
    user_agent = request.headers.get('User-Agent')
    async with SessionLocal() as session:
        await session.execute(
            "INSERT INTO counters(datetime, client_info, value) "
            f"VALUES ('{date}','{user_agent}',{store['count']})")
        await session.commit()
    return store['count']


@app.get("/stat")
async def counter(request: Request):
    """
    Метод обрабатывающий путь /stat
    :param request: значение реквеста
    :return: значение счетчика + 1
    """
    store["count"] = store["count"] + 1
    date = datetime.datetime.now().isoformat()
    user_agent = request.headers.get('User-Agent')
    async with SessionLocal() as session:
        await session.execute(
            "INSERT INTO counters(datetime, client_info, value) "
            f"VALUES ('{date}','{user_agent}',{store['count']})")
        await session.commit()

    return store["count"]


@app.get("/about")
async def say_hello():
    """
    Метод обрабатывающий путь /about
    :param request: значение реквеста
    :return: инфу об учащемся
    """
    name = "Mikhail Ivanov"
    html = f"<h3>Hello, {name}!</h3>"
    return HTMLResponse(content=html, status_code=200)


@app.on_event("startup")
async def startup_event():
    """
    Метод работающий при запуске приложения
    делает запрос к субд для восстановления
    значения счетчика по последней записи
    из таблицы counters
    """
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
            "SELECT value FROM counters ORDER BY datetime DESC LIMIT 1")
        count = res.scalar()
        if not count:
            store["count"] = 0
        else:
            store["count"] = count
