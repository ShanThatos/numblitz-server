from pathlib import Path

from sqla_wrapper import Alembic

import alembic
from src import config

from .main import db
from .models import *


def migrate():
    env = config.get("ENVIRONMENT")
    alembic_folder = Path(f"alembic/{env}-migrations/")
    alembic_folder.mkdir(parents=True, exist_ok=True)
    al = Alembic(db, alembic_folder)
    al.init(alembic_folder)
    try:
        script = al.revision("<update_message>")
        if (
            input(
                f"Migration Script: {script.path if script else '<none>'} Continue? [y/n] (y)"
            ).lower()
            == "n"
        ):
            return
        al.upgrade()
    except alembic.util.exc.CommandError as e:  # type: ignore
        print(e)

        if str(e).startswith("Target database is not up to date."):
            if input("Attempt fix? [y/n] (y)").lower() in ("", "y"):
                al.stamp()


if __name__ == "__main__":
    migrate()
