from sqla_wrapper import SQLAlchemy

from src import config

db = SQLAlchemy(config.get("DATABASE_URL"), engine_options={"pool_pre_ping": True})


__all__ = ("db",)
