import json

from sqla_wrapper.session import Session

from .. import ProblemCategory, db

with open("categories.json", "r") as f:
    categories = json.load(f)


with db.Session() as dbs:
    dbs: Session
    for category in categories:
        instance = dbs.get(ProblemCategory, category["id"])
        if instance is None:
            instance = dbs.create(ProblemCategory, **category)
            print(f"Created new category: {instance.id} {instance.name}")
        else:
            instance.name = category["name"]
            instance.display = category["display"]
            print(f"Updated category: {instance.id} {instance.name}")
        dbs.commit()


# poetry run python -m src.database.scripts.add_update_categories --dev
