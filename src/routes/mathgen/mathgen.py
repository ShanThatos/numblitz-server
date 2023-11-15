from typing import Annotated, Optional

from fastapi import Depends
from mathgen import MathProblemGenerator

from src.base.fastapi_instance import app
from src.database.models import ProblemCategory, ProblemModel
from src.utils.auth.depend import AuthUser, any_user
from src.utils.jinja.jinja_utils import render_template


@app.get("/mathgen/categories")
def mathgen_categories():
    return ProblemCategory.all_as_dict()


@app.get("/mathgen/category/{category_id}")
def mathgen_category(category_id: str):
    return ProblemCategory.get(category_id).as_dict()


@app.get("/mathgen/models")
def mathgen_models(
    auser: Annotated[AuthUser, Depends(any_user)],
    category_id: Optional[str] = None,
    model_ids: Optional[str] = None,
):
    expressions = []
    if category_id is not None:
        expressions.append(ProblemModel.category_id == category_id)
    if model_ids is not None:
        expressions.append(ProblemModel.id.in_(model_ids.split(",")))

    models = ProblemModel.all(*expressions)
    return [model.get_public_data(auser.subscribed) for model in models]


@app.get("/mathgen/model/{model_id}/explanation")
def mathgen_model_explanation(auser: Annotated[AuthUser, Depends(any_user)], model_id: str):
    model = ProblemModel.get(model_id)

    if not model.allow_access(auser.subscribed):
        return ":("

    return render_template("mathviews/explanation.html", contents=model.explanation)


@app.get("/mathgen/model/{model_id}/problems")
def mathgen_model_problem(
    auser: Annotated[AuthUser, Depends(any_user)], model_id: str, count: int = 1
):
    model = ProblemModel.get(model_id)

    if not model.allow_access(auser.subscribed):
        return ":("

    return MathProblemGenerator.from_code(model.code).generate_multiple(count)
