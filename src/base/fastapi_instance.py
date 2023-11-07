from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from src import config
from src.database import db

from .lifespan import lifespan

app = FastAPI(lifespan=lifespan)
app.add_middleware(SessionMiddleware, secret_key=config.get("SECRET_KEY"))
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def remove_db_scoped_session(request: Request, call_next):
    response = await call_next(request)
    db.s.remove()
    return response


__all__ = ("app",)
