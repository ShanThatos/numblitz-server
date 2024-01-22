from typing import Annotated

from fastapi import Depends

from src.base.fastapi_instance import app
from src.database import db
from src.database.models import ModelProgress, ProblemModel
from src.utils.auth.depend import AuthUser, any_user


@app.get("/mathgen/modelprogress")
def mathgen_modelprogress(auser: Annotated[AuthUser, Depends(any_user)], model_ids: str):
    if auser.is_guest:
        return {}

    model_ids = model_ids.strip()
    if not model_ids:
        return {}

    mps = ModelProgress.all(
        ModelProgress.user_id == auser.user.id,
        ModelProgress.model_id.in_(model_ids.split(",")),
    )

    progress = {}
    for mp in mps:
        progress[mp.model_id] = {"progress": mp.progress, "average": mp.average_time}

    return progress


@app.post("/mathgen/modelprogress/{model_id}")
def mathgen_modelprogress_post(
    auser: Annotated[AuthUser, Depends(any_user)], model_id: str, progress: int, average_time: float
):
    if auser.is_guest:
        return {}

    model = ProblemModel.get(model_id)
    if not model.allow_access(auser.subscribed):
        return {}

    mp: ModelProgress = db.s.first_or_create(
        ModelProgress, user_id=auser.user.id, model_id=model_id
    )
    mp.progress = progress
    mp.average_time = average_time
    db.s.commit()

    return {}
