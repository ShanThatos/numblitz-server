import traceback
from typing import Annotated

from fastapi import Depends, Form, Response
from fastapi.responses import HTMLResponse
from mathgen import MathProblemModel

from src.base.fastapi_instance import app
from src.database import ProblemCategory, ProblemModel, db
from src.routes.admin.verify import verify_admin
from src.utils.jinja.jinja_utils import render_macro, render_template
from src.utils.mathgen import generate_multiple


@app.get("/admin/listmodels", dependencies=[Depends(verify_admin)])
def admin_listmodels():
    return HTMLResponse(
        render_template(
            "admin/listmodels.html", models=ProblemModel.all(), categories=ProblemCategory.all()
        )
    )


@app.get("/admin/createmodel", dependencies=[Depends(verify_admin)])
def admin_createmodel():
    return HTMLResponse(
        render_template(
            "admin/editmodel.html",
            model=None,
            categories=ProblemCategory.all(),
        )
    )


@app.get("/admin/editmodel/{model_id}", dependencies=[Depends(verify_admin)])
def admin_editmodel(model_id: str):
    return HTMLResponse(
        render_template(
            "admin/editmodel.html",
            model=ProblemModel.get(model_id),
            categories=ProblemCategory.all(),
        )
    )


@app.get("/admin/modelexplanation/{model_id}", dependencies=[Depends(verify_admin)])
def admin_modelexplanation(model_id: str):
    return ProblemModel.get(model_id).explanation


def model_form_data(
    id: Annotated[str, Form()],
    category_id: Annotated[str, Form()] = "",
    name: Annotated[str, Form()] = "",
    display: Annotated[str, Form()] = "",
    difficulty: Annotated[str, Form()] = "1",
    unlocked: Annotated[str, Form()] = "off",
    code: Annotated[str, Form()] = "",
    explanation: Annotated[str, Form()] = "",
    answer_format: Annotated[str, Form()] = "auto",
    rtl: Annotated[str, Form()] = "off",
    units: Annotated[str, Form()] = "",
    hidden: Annotated[str, Form()] = "off",
):
    return {
        "id": id,
        "category_id": category_id,
        "name": name,
        "display": display,
        "difficulty": int(difficulty),
        "unlocked": unlocked == "on",
        "code": code,
        "explanation": explanation,
        "answer_format": answer_format,
        "rtl": rtl == "on",
        "units": units,
        "hidden": hidden == "on",
    }


@app.post("/admin/savemodel/{original_id}", dependencies=[Depends(verify_admin)])
async def admin_savemodel(original_id: str, form_data: Annotated[dict, Depends(model_form_data)]):
    new_id = form_data["id"]
    if new_id != original_id:
        if ProblemModel.get_or_none(new_id) is not None:
            return Response(
                "Duplicate model id",
                headers={"HX-Reswap": "innerHTML", "HX-Retarget": "#error-message"},
            )

    original_model = ProblemModel.get_or_none(original_id)
    model = original_model
    if model is None:
        model = ProblemModel(id=original_id)
    model.id = form_data["id"]
    model.category_id = form_data["category_id"]
    model.name = form_data["name"]
    model.display = form_data["display"]
    model.difficulty = form_data["difficulty"]
    model.unlocked = form_data["unlocked"]
    model.code = form_data["code"]
    model.explanation = form_data["explanation"]
    model.answer_format = form_data["answer_format"]
    model.rtl = form_data["rtl"]
    model.units = form_data["units"]
    model.hidden = form_data["hidden"]

    if original_model is None:
        db.s.add(model)
    db.s.commit()

    return Response(headers={"HX-Redirect": "/admin/editmodel/" + model.id})


@app.post("/admin/mathgen/generate", dependencies=[Depends(verify_admin)])
def admin_generate(form_data: Annotated[dict, Depends(model_form_data)]):
    try:
        problems = generate_multiple(
            model=MathProblemModel(
                id="generated_from_code",
                code=form_data["code"],
                format=form_data["answer_format"],
            ),
            count=5,
        )

        return HTMLResponse(
            "\n".join(
                render_macro("admin/problem.html:math_problem", p, units=form_data["units"])
                for p in problems
            )
        )
    except Exception as e:
        return HTMLResponse(str(e))
